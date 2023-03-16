import re
import allure
import docker
import pytest
from typing import final, List
from datetime import datetime, timedelta
from _pytest.mark.structures import Mark
from allure_pytest.listener import AllureListener
from yaf.fabric.ClientsConfig import ClientStore
from yaf.fabric.clientTypes.SqlDbClient import SqlDbCl
from yaf.data.data_prepare import CollectedTests
from yaf.utils.common_constants import TEST_DATA, JIRA_PATH
from yaf.app.test_util import set_allure_listener
from yaf.app.tests import executor
from yaf.steps.base_operations import Base
from docker.errors import NotFound as ContainerNotFound


Run: final(CollectedTests) = CollectedTests()


def pytest_collection_modifyitems(config, items):
    set_allure_listener(next(p for p in config.pluginmanager.get_plugins() if isinstance(p, AllureListener)))
    for item in items:
        if item.originalname.startswith('tests_'):
            item.name = item.name.replace('tests_', '').upper()
            item._nodeid = item._nodeid.replace(item.originalname, item.name)
        if item.originalname == 'test_':
            entity = item.callspec.params['_generator_']
            item.own_markers.append(Mark('allure_label', tuple([entity['feature']]), {'label_type': 'feature'}))
            item.own_markers.append(Mark('allure_label', tuple([entity['epic']]), {'label_type': 'epic'}))
            # TODO:: jira key as tag
            if 'jira' in entity:
                entity['name'] = f'({entity["jira"]}) - {entity["name"]}'
                item.own_markers.append(Mark('allure_link', tuple([f'{JIRA_PATH}/{entity["jira"]}']),
                                             {'name': entity["jira"], 'link_type': 'test_case'}))
            if 'flaky' in entity:
                for i in range(len(item.own_markers)):
                    if item.own_markers[i].name == 'flaky':
                        item.own_markers[i] = Mark('flaky', (), {'reruns': entity['flaky']})
            if 'tags' in entity:
                for tag in entity['tags']:
                    item.own_markers.append(Mark(tag, (), {}))
                item.own_markers.append(Mark('allure_label', tuple(entity['tags']), {'label_type': 'tag'}))
            item.name = entity['name']
            item._nodeid = re.sub(r'test_\[.+]', item.name, item.nodeid)
            item.user_properties.append(entity['steps'])
            item.user_properties.append(entity['before'])
            item.user_properties.append(entity['after'])
            if 'params' in entity:
                test_data_row = entity['params']
                item.user_properties.append(test_data_row)
                for param in entity['params']:
                    item.callspec.params[param] = test_data_row[param]
                item.callspec.params['_generator_'] = "multi"
            else:
                item.callspec.params['_generator_'] = "single"
                item.user_properties.append({})


@pytest.fixture(scope='session')
def session_preparation(worker_id):
    print(f"\n*** CREATE CONNECTION POOL FOR <{worker_id}> ***")
    Base.connections = ClientStore(Run.config_set)
    allure.attach(Base.connections.connect_yml_text, 'CONNECTIONS', allure.attachment_type.YAML)
    if worker_id == 'master':
        _before_after_processor(0)
    yield Base.connections
    if worker_id == 'master':
        _before_after_processor(1)
    Base.connections.finalize()
    print(f"\n*** TERMINATE CONNECTION POOL FOR <{worker_id}> ***")


@pytest.fixture
def instructions(session_preparation, request):
    print("\n*** Test Start ***")
    print(f"*** {session_preparation} ***")
    start = datetime.utcnow()
    try:
        _prepare_sql_clients(is_start=True)
        executor(request.node.user_properties[1])
        yield
        executor(request.node.user_properties[2])
        _prepare_sql_clients(is_start=False)
    except Exception as ex:
        allure.attach(str(ex), f'Catch exception: {str(type(ex))} !!',
                      allure.attachment_type.TEXT)
        raise ex
    finally:
        attach_container_log(Base.connections.log_listener, start)
        Base.reset()
        print("\n*** Test Finish ***")


@pytest.fixture
def _setup_(worker_id):
    before_after_in_parallel(slave_id=worker_id, num_set=0)


@pytest.fixture(params=Run.test_set)
def _generator_(request):
    Base.stash[TEST_DATA] = request.node.user_properties[3]
    return request.node.user_properties[0]


@pytest.fixture
def _teardown_(worker_id):
    before_after_in_parallel(slave_id=worker_id, num_set=1)


########################################################################################################################

def before_after_in_parallel(slave_id: str, num_set: int):
    if slave_id == 'master':
        Base.connections = ClientStore(Run.config_set)
        _before_after_processor(num_set)
        Base.connections.finalize()


def _before_after_processor(num_instructions: int):
    try:
        _prepare_sql_clients(is_start=True)
        for feature in Run.preset_teardown:
            executor(Run.preset_teardown[feature][num_instructions])
        _prepare_sql_clients(is_start=False)
    except Exception as exc:
        Base.connections.finalize()
        raise Exception(f'{exc}')
    finally:
        if num_instructions == 0:
            Base.stash = {f'setup.once.before.{k}': v for (k, v) in Base.stash.items()}
        Base.reset()


def _prepare_sql_clients(is_start: bool):
    bus = Base.connections.clients_bus
    for cl_name in bus:
        if isinstance(bus[cl_name], SqlDbCl):
            bus[cl_name].launch_session() if is_start else bus[cl_name].shutdown_session()


def attach_container_log(containers: List[str], start_time: datetime):
    if len(containers) > 0:
        with allure.step('Логи указанных Docker контейнеров'):
            log_time = (start_time + timedelta(hours=3)).strftime('%H:%M:%S. %f')
            docker_cl = docker.from_env()
            for container in containers:
                try:
                    container_logs = docker_cl.containers.get(container) \
                        .logs(since=start_time).decode("utf-8")
                    allure.attach(container_logs,
                                  f'Received logs from [{container}] '
                                  f'approximately since {log_time}',
                                  allure.attachment_type.TEXT)
                except ContainerNotFound as nex:
                    allure.attach(str(nex), f'Container [{container}] Not Found !!',
                                  allure.attachment_type.TEXT)
