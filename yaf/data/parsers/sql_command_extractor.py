import re
from yaf.fabric.clientTypes.SqlDbClient import ResultSet
from yaf.utils.regex_operations import single_regex_find, single_regex_find_non_none
from yaf.utils.injection_ops import evaluate_injection
from yaf.utils.common_constants import SQL_MARK


def parse(text):
    return {'row':    extract_row(text),
            'column': extract_column(text)}


def extract_row(text):
    return single_regex_find(
        text=text,
        regex=r'ROW: (\d+|ALL)')


def extract_column(text):
    return single_regex_find_non_none(
        text=text,
        regex=r'COLUMN: (\S+)',
        not_found_msg='Отсутствует COLUMN!')


def extract_transform_expr(text):
    result = re.search(r'(TRANSFORM:|=>>|->>|->) (.+)', text)
    return result.group(2) if result else False


def get_value_from_stash(text, stash: dict):
    if isinstance(text, str) and re.match(SQL_MARK, text):
        result: ResultSet = stash[re.findall(r'SQL_RS_\d+', text).pop()]
        answer = result.get_cell_value(column=extract_column(text), row=extract_row(text))
        action = extract_transform_expr(text)
        return evaluate_injection(expression=action, this=answer) if action else answer
    return text
