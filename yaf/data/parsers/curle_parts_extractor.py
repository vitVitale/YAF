import re
from yaf.utils.regex_operations import single_regex_find_non_none


def parse_curl(curl):
    return {'method':   extract_http_method(curl),
            'url':      extract_url(curl),
            'headers':  extract_headers(curl),
            'body':     extract_body(curl)}


def extract_http_method(curl):
    return single_regex_find_non_none(
        text=curl,
        regex=r'-X (GET|POST|PUT|DELETE|PATCH) ',
        not_found_msg='в cURL запросе отсутствует HttpMethod!')


def extract_url(curl):
    return single_regex_find_non_none(
        text=curl,
        regex=r' \'(http.+)\'',
        not_found_msg='в cURL запросе отсутствует URL!')


def extract_headers(curl):
    headers_dict = {}
    for _, key, value in re.findall(r'-H \'((.+): (.+))\'', curl):
        headers_dict[key] = value
    return headers_dict


def extract_body(curl):
    try:
        return re.findall(r'-d \'(.+)\'', curl, re.DOTALL).pop()
    except IndexError as e:
        print('в cURL запросе отсутствует body!')
        return None
