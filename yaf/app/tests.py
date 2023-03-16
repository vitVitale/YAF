import re
import pytest
from typing import final, Type
from importlib import import_module
from yaf.steps.context import BaseContext
from yaf.utils.common_constants import RERUN_COUNTER, CUSTOM_CTX
from yaf.app.test_util import skip_step_instruction, iterate_step_instruction, \
                                 exec_step_instruction, verify_condition


def include_custom_context():
    try:
        clazz = import_module(CUSTOM_CTX).CustomContext
        assert issubclass(clazz, BaseContext), \
            f'Класс [{CUSTOM_CTX}] не является наследуемым от [steps.context.BaseContext]'
        # TODO:: add sys path to extension dir
        return clazz
    except:
        return BaseContext


ctx: final(Type[BaseContext]) = include_custom_context()


def executor(steps):
    if isinstance(steps, list):
        for step in steps:
            invoke_flag = False
            for method, signature in ctx.register.items():
                if re.fullmatch(r'{}'.format(signature), step['command']):
                    invoker = getattr(ctx, method)
                    invoke_flag = True
                    client_name = re.sub(r'.+-', '', step['command'])
                    args = [arg for arg in [
                        client_name if client_name != step['command'] else None,
                        step['params'].get("text", None),
                        step['params'].get("expected", None)
                    ] if arg is not None]
                    if 'optional_by' in step and not verify_condition(step.get('optional_by', True)):
                        skip_step_instruction(step)
                        break
                    if 'iterable_by' in step:
                        iterate_step_instruction(step, invoker, args)
                        break
                    exec_step_instruction(step, invoker, args)
                    break
            if not invoke_flag:
                raise Exception(f'Метод [{step["command"]}] не существует!')


########################################################################################################################

class TestRunner:

    def tests_before_all(self, _setup_):
        pass

    @pytest.mark.flaky(reruns=RERUN_COUNTER)
    def test_(self, _generator_, instructions):
        executor(_generator_)

    def tests_after_all(self, _teardown_):
        pass
