from yaf.utils.regex_operations import single_regex_find, single_regex_find_non_none


def parse(text):
    return {'index':    extract_index(text),
            'doc_type': extract_type(text),
            'query':    extract_query(text),
            'id':       extract_id(text),
            'kql':      extract_kibana_query(text),
            'before':   extract_time_delta(text),
            'field':    extract_default_search_field(text)}


def extract_index(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'INDEX: (.+)',
        not_found_msg='Index not specified !')


def extract_type(text):
    return single_regex_find(
        text=text,
        regex=r'TYPE: (.+)')


def extract_id(text):
    return single_regex_find(
        text=text,
        regex=r'ID: (.+)')


def extract_query(text):
    return single_regex_find(
        text=text,
        regex=r'QUERY: (.+)')


def extract_kibana_query(text):
    return single_regex_find(
        text=text,
        regex=r'KQL: (.+)')


def extract_default_search_field(text):
    return single_regex_find(
        text=text,
        regex=r'FIELD: (.+)')


def extract_time_delta(text):
    result = single_regex_find(
        text=text,
        regex=r'BEFORE: (\d+(s|m|h|d|w|M))')
    return result[0] if result is not None else result
