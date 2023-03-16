import re
from yaf.utils.regex_operations import single_regex_find
from yaf.utils.common_constants import EMPTY


def parse(text):
    return {'header':   extract_headers(text),
            'endpoint': extract_endpoint(text),
            'timeout':  extract_timeout(text),
            'get':      extract_get(text)}


def extract_timeout(text):
    timeout = single_regex_find(text=text, regex=r'TIMEOUT: (\d+)')
    if timeout:
        return int(timeout)/1000
    return 5


def extract_endpoint(text):
    res = single_regex_find(
        text=text,
        regex=r'ENDPOINT: (.*)')
    return res if res else EMPTY


def extract_get(text):
    return single_regex_find(
        text=text,
        regex=r'GET: (NEXT|LAST)')


def extract_headers(text):
    headers = []
    for value in re.findall(r'HEADER: (.+)', text):
        headers.append(value)
    return headers
