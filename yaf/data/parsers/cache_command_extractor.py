import re
from yaf.utils.regex_operations import single_regex_find, single_regex_find_non_none


def parse(text):
    return {'scheme':   extract_scheme(text),
            'key':      extract_key(text),
            'value':    extract_value(text),
            'expired':  extract_expired(text),
            'allIn':    is_all_in(text)}


def extract_scheme(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'SCHEME: (.+)',
        not_found_msg='Missing SCHEME!')


def extract_key(text):
    return single_regex_find(
        text=text,
        regex=r'KEY: (.+)')


def extract_expired(text):
    return single_regex_find(
        text=text,
        regex=r'EXPIRED: (\d+)')


def extract_value(text):
    try:
        return re.findall(r'VALUE: (.+)', text, re.DOTALL).pop()
    except IndexError as e:
        return None


def is_all_in(text):
    return single_regex_find(
        text=text,
        regex=r'(ALLIN)') is not None
