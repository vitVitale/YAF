import re
import yaml
from os.path import isfile
from jinja2 import Template
from yaf.utils.common_constants import ENV_FILE, EMPTY, STRUCT_MARK
from yaf.utils.injection_ops import evaluate_injection
from yaf.utils.time_operations import now


func_dict = {
    "now": now
}


def process_jinja_template(query):
    if isinstance(query, str):
        matches = re.findall(r'(time|math):(\w+\(.*\))', query)
        if len(matches) > 0:
            template = Template(f'{{{{ {matches.pop()[1]} }}}}')
            template.globals.update(func_dict)
            return template.render()
    return query


def get_object_from_stash(query, stash):
    if isinstance(query, str) and query.startswith(STRUCT_MARK):
        str_mass = query.split(' : ')
        struct = stash[str_mass[1]]
        if len(str_mass) == 2:
            return struct
        if len(str_mass) == 3:
            try:
                joiner = '.' if not isinstance(struct, tuple([list, dict])) else EMPTY
                return eval(f'struct{joiner}{str_mass[2]}')
            except AttributeError:
                raise AssertionError(f'Не верный путь: [ {str_mass[2]} ] \n'
                                     f'для структуры [ {str_mass[1]} ] !')
    return query


def get_variable_from_stash(query, stash):
    if isinstance(query, str) and re.findall(r'(env|global|iterator)\..+', query):
        query_parts = query.split(' : ')
        answer = stash[query_parts[0]]
        if len(query_parts) == 2:
            answer = evaluate_injection(expression=query_parts[1],
                                        this=answer)
        return answer
    return query


def get_variable_from_env_file(query):
    if isinstance(query, str) and query.startswith('env_file.'):
        query_parts = query.split(' : ')
        assert isfile(ENV_FILE), f"Значение переменной [{query_parts[0]}] не найдено " \
                                 f"т.к. отсутствует __env_file__.yml !"
        with open(ENV_FILE, "r", encoding='utf-8') as stream:
            try:
                envs_map: dict = yaml.safe_load(stream)
                var_name_in_file = query_parts[0].replace('env_file.', EMPTY)
                answer = envs_map.get(var_name_in_file)
                assert answer, f"Переменная {var_name_in_file} отсутствует в ENV_FILE!"
                if len(query_parts) == 2:
                    answer = evaluate_injection(expression=query_parts[1],
                                                this=answer)
                return answer
            except yaml.YAMLError as exc:
                raise Exception(f'Не удалось распарсить файл {ENV_FILE} \n{exc.__cause__}')
            except AssertionError as aex:
                raise Exception(aex)
    return query
