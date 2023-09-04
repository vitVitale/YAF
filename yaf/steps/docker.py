import allure
import docker
import subprocess
from time import sleep
from .base_operations import Base
from yaf.utils.common_constants import RESOURCES_DIR
from yaf.data.parsers.docker_command_extractor import parse


class DockerSteps(Base):

    @staticmethod
    @allure.step('Control ST environment')
    def control_st_environment(text):
        parsed_dict = parse(DockerSteps.render_and_attach(text))
        timeout = parsed_dict['timeout']
        timeout = int(timeout) if timeout else 10
        rollup, command = DockerSteps._compose_runner(parsed_dict["compose_file"],
                                                      parsed_dict["type"])
        try:
            result = DockerSteps._run_command(command, timeout)
        except subprocess.CalledProcessError as ex:
            raise Exception(f'Call error for cmd:\n{ex.cmd}\n'
                            f'Causes:\n{ex.stderr.decode("utf-8")}')
        result = f'{result.stderr.decode("utf-8")}'
        info_mess = 'Received console log - \n'
        DockerSteps.attach_request_block(info_mess=info_mess,
                                         save=False,
                                         body=result)
        if rollup:
            DockerSteps._container_waiter(container=parsed_dict['wait_for'],
                                          check=parsed_dict['ready_check'],
                                          timeout=timeout)

########################################################################################################################

    @staticmethod
    def _compose_runner(compose, action):
        cmd = f'docker-compose -f {compose} {action.lower()}'
        allure.attach(open(f'{RESOURCES_DIR}/{compose}').read(),
                      'compose file - \n', allure.attachment_type.TEXT)
        if 'UP' == action.upper():
            return True, f'{cmd} --detach'
        elif 'RESTART' == action.upper():
            return True, f'{cmd[:-7]}up --force-recreate --detach'
        elif 'DOWN' == action.upper():
            return False, f'{cmd} -v --remove-orphans'

    @staticmethod
    def _container_waiter(container, check, timeout):
        if container and check:
            container_logs = None
            docker_cl = docker.from_env()
            for _ in range(timeout):
                sleep(1)
                container_logs = docker_cl.containers.get(container).logs().decode("utf-8")
                if check in container_logs:
                    allure.attach(f'{container.upper()} IS READY !!', 'Healthcheck - \n', allure.attachment_type.TEXT)
                    return
            allure.attach(container_logs, f'Healthcheck UNREACHABLE [{timeout} sec.] !!!  - \n',
                          allure.attachment_type.TEXT)
            raise Exception(f'Failed to verify {container} viability for {timeout} seconds.\n'
                            f'Possible errors in the container logs.')

    @staticmethod
    def _run_command(command, timeout):
        return subprocess.run(command, cwd=RESOURCES_DIR,
                              capture_output=True,
                              timeout=timeout,
                              check=True,
                              shell=True)
