import re
from json import loads
from yaf.utils.regex_operations import single_regex_find


def jwt_parse(text):
    return {'algorithm': extract_algorithm(text),
            'key':       extract_key(text),
            'data':      extract_data(text)}


def extract_algorithm(text):
    result = single_regex_find(
        text=text,
        regex=r'ALGORITHM: (.+)')
    return None if result == 'None' else result


def extract_key(text):
    result = single_regex_find(
        text=text,
        regex=r'KEY: (.+)')
    return None if result == 'None' else result


def extract_data(text):
    try:
        return loads(re.findall(r'DATA: (.+)', text, re.DOTALL).pop())
    except Exception as e:
        raise Exception('Failed to extract and parse data!')
