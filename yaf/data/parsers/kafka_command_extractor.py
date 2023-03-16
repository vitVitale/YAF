import re
from yaf.utils.regex_operations import single_regex_find


def parse(text):
    return {'partition':    extract_partition(text),
            'topic':        extract_topic(text),
            'key':          extract_key(text),
            'headers':      extract_headers(text),
            'avro_schema':  extract_avro_schema(text),
            'message':      extract_message(text),
            'marker':       extract_marker(text)}


def extract_partition(text):
    result = single_regex_find(
        text=text,
        regex=r'PARTITION: (\d+)')
    return int(result) if result else -1


def extract_avro_schema(text):
    return single_regex_find(
        text=text,
        regex=r'AVRO_SCHEMA: (.+)')


def extract_marker(text):
    return single_regex_find(
        text=text,
        regex=r'MARKER: (.+)')


def extract_topic(text):
    return single_regex_find(
        text=text,
        regex=r'TOPIC: (.+)')


def extract_key(text):
    return single_regex_find(
        text=text,
        regex=r'KEY: (.+)')


def extract_headers(text):
    headers_dict = {}
    for key, value in re.findall(r'HEADER: \[ (.+) :: (.+) ]', text):
        headers_dict[key] = value
    return headers_dict


def extract_message(text):
    try:
        return re.findall(r'MESSAGE: (.+)', text, re.DOTALL).pop()
    except IndexError as e:
        print('Отсутствует тело для отправки!')
        return None
