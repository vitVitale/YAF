import re
from yaf.utils.regex_operations import single_regex_find


def parse(text):
    return {'database':   extract_db(text),
            'collection': extract_collection(text),
            'fields':     extract_fields(text),
            'filter':     extract_filter(text),
            'value':      extract_value(text),
            'sort':       extract_sort(text)}


def extract_db(text):
    return single_regex_find(
        text=text,
        regex=r'DATABASE: (.+)')


def extract_collection(text):
    return single_regex_find(
        text=text,
        regex=r'COLLECTION: (.+)')


def extract_fields(text):
    return single_regex_find(
        text=text,
        regex=r'FIELDS: (.+)')


def extract_filter(text):
    return single_regex_find(
        text=text,
        regex=r'FILTER: (.+)')


def extract_sort(text):
    match = single_regex_find(text=text, regex=r'SORT: (.+)\((ASC|DESC)\)')
    if match:
        sort_rule = list(match)
        sort_rule[1] = 1 if sort_rule[1] == 'ASC' else -1
        return sort_rule
    return ['_id']


def extract_value(text):
    try:
        return re.findall(r'VALUE: (.+)', text, re.DOTALL).pop()
    except IndexError as e:
        return None
