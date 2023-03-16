import os
from re import fullmatch
from json import dumps, loads
from jsonpath_ng.ext import parse
from .common_constants import JPATH_MARK, GET_FILE_MARK, EMPTY, TEST_DATA, RESOURCES_DIR, HEADERS_MARK
from .injection_ops import evaluate_injection


def get_value_from_object_of_stash(query, stash):
    if isinstance(query, str) and query.startswith(JPATH_MARK):
        str_mass = query.split(' : ')
        if len(str_mass) > 2:
            try:
                json_path = parse(str_mass[2])
                tree = str_mass[1].split(':>:')
                struct = stash[tree[0]]
                doc = loads(evaluate_injection(str_mass[1].replace(tree[0], 'struct'), struct=struct))
                results = [x.value for x in json_path.find(doc)]
                answer = results if len(results) > 1 else results[0]
                if len(str_mass) == 4:
                    answer = evaluate_injection(expression=str_mass[3],
                                                this=answer)
                query = answer
            except KeyError:
                raise Exception(f'Отсутствует документ по маркеру [ {str_mass[1]} ] !')
            except IndexError:
                raise AssertionError(f'Значения для jsonPath: [ {str_mass[2]} ] \n'
                                     f'не найдены в документе [ {str_mass[1]} ] !')
    return query


def get_header_value(query, stash):
    if isinstance(query, str) and fullmatch(HEADERS_MARK, query):
        str_mass = query.split(' : ')
        mark, key = (str_mass[0], str_mass[1])
        try:
            query = stash[mark][key]
        except KeyError:
            raise Exception(f'Отсутсвует заголовок [ {key} ] !')
    return query


def get_resources_file(path):
    if isinstance(path, str) and path.startswith(GET_FILE_MARK):
        path = f'{RESOURCES_DIR}/{path.replace(GET_FILE_MARK, EMPTY)}'
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as file:
                path = file.read()
    return path


def get_from_test_data(key: str, stash):
    try:
        return stash[TEST_DATA][key]
    except KeyError as e:
        raise Exception(f'В test_data отсутсвует значение для шаблона {key} !!')


def is_payload_json(json_candidate):
    try:
        loads(json_candidate)
        return True
    except:
        return False
