import re
from yaf.utils.regex_operations import single_regex_find_non_none


def parse(text):
    return {'service': extract_service(text),
            'method':  extract_method(text),
            'args':    extract_args(text)}


def extract_service(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'SERVICE: (.+)',
        not_found_msg='Отсутствует SERVICE!')


def extract_method(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'METHOD: (.+)',
        not_found_msg='Отсутствует METHOD!')


def extract_args(text):
    try:
        return re.findall(r'ARGS: (.+)', text, re.DOTALL).pop()
    except IndexError as e:
        return None
