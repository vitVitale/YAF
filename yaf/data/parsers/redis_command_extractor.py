import re
from yaf.utils.regex_operations import single_regex_find, single_regex_find_non_none


def parse(text):
    return {'key':      extract_key(text),
            'value':    extract_value(text),
            'expired':  extract_expired(text)}


def extract_key(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'KEY: (.+)',
        not_found_msg='Missing KEY!')


def extract_expired(text):
    return single_regex_find(
        text=text,
        regex=r'EXPIRED: (\d+)')


def extract_value(text):
    try:
        return re.findall(r'VALUE: (.+)', text, re.DOTALL).pop()
    except IndexError as e:
        return None
