from yaf.utils.regex_operations import single_regex_find, single_regex_find_non_none


def parse(text):
    return {'compose_file': extract_compose_file(text),
            'type':         extract_type(text),
            'wait_for':     extract_wait_for(text),
            'timeout':      extract_timeout(text),
            'ready_check':  extract_ready_check(text)}


def extract_compose_file(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'COMPOSE: (.+)',
        not_found_msg='docker-compose file not specified!')


def extract_type(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'TYPE: (?i)(UP|DOWN|RESTART)',
        not_found_msg='Operation not set!')


def extract_wait_for(text):
    return single_regex_find(
        text=text,
        regex=r'WAIT_FOR: (.+)')


def extract_timeout(text):
    return single_regex_find(
        text=text,
        regex=r'TIMEOUT: (\d+)')


def extract_ready_check(text):
    return single_regex_find(
        text=text,
        regex=r'READY_CHECK: (.+)')
