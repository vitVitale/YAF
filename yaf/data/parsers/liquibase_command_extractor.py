from yaf.utils.regex_operations import single_regex_find, single_regex_find_non_none


def parse(text):
    return {'changelog':   extract_changelog(text),
            'contexts':    extract_contexts(text),
            'schema':      extract_schema(text),
            'task':        extract_task(text)}


def extract_changelog(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'CHANGELOG: (.+)',
        not_found_msg='Не указан changelog master файл !')


def extract_task(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'TASK: (.+)',
        not_found_msg='Не указана операция !\n'
                      'Примеры: [update, dropAll]')


def extract_schema(text):
    return single_regex_find(
        text=text,
        regex=r'SCHEMA: (.+)')


def extract_contexts(text):
    return single_regex_find(
        text=text,
        regex=r'CONTEXTS: (.+)')
