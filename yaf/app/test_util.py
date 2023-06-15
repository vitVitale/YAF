import allure
from time import sleep
from contextlib import nullcontext
from allure_commons.model2 import Status
from allure_commons.utils import uuid4, now
from allure_pytest.listener import AllureListener
from yaf.utils.injection_ops import evaluate_injection
from yaf.steps.base_operations import Base


allure_listener_obj: AllureListener


def set_allure_listener(value):
    global allure_listener_obj
    allure_listener_obj = value


def verify_condition(param) -> bool:
    return evaluate_injection(expression=f"({Base.perform_replacement_and_return(param)}) == True")


def skip_step_instruction(step: dict):
    idx = uuid4()
    allure_listener_obj \
        .start_step(idx, f'!! SKIPPED STEP !! [ {step.get("allure_step", step["command"])} ]', {})
    allure_listener_obj.allure_logger \
        .stop_step(idx, stop=now(), status=Status.SKIPPED)


def iterate_step_instruction(step: dict, invoker, args):
    iterable_block = step.get('iterable_by')
    delay = iterable_block.get('delay', 0) / 1000
    interruption = iterable_block.get('interruption', False)
    freeze_counters = iterable_block.get('stop_rq_rs_counter', False)
    collection = Base.perform_replacement_and_return(iterable_block.get('collection')) \
        if isinstance(iterable_block.get('collection'), str) else iterable_block.get('collection')
    retry = iterable_block.get('retry')
    if retry:
        assert retry > 0, 'Количество повторов [iterable_by.retry] должно быть больше 0 !'
        assert interruption, 'Для повторов необходимо указать условие прерывания в [iterable_by.collection] !'
        collection = [_ for _ in range(retry)]
        freeze_counters = True

    def perform_step():
        invoker(*args)
        if freeze_counters:
            Base.sqlRsCounter -= 1
            Base.rqCounter -= 1
            Base.rsCounter -= 1
        if interruption and verify_condition(interruption):
            raise InterruptedError
        sleep(delay)

    with allure.step(step['allure_step']) \
            if step.get('allure_step') else nullcontext():
        try:
            match collection:
                case _ if isinstance(collection, (list, tuple)):
                    for item in collection:
                        Base.stash['iterator.value'] = item
                        perform_step()
                case _ if isinstance(collection, dict):
                    for key, val in collection.items():
                        Base.stash['iterator.value'] = val
                        Base.stash['iterator.key'] = key
                        perform_step()
                case _:
                    raise Exception('Не итерируемое значение в [iterable_by.collection] !')
            if interruption:
                raise AssertionError("Условие из [iterable_by.interruption] не достигнуто !")
        except InterruptedError:
            pass


def exec_step_instruction(step: dict, invoker, args):
    with allure.step(step['allure_step']) \
            if step.get('allure_step') else nullcontext():
        invoker(*args)
