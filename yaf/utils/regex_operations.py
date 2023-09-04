import re
from rstr import xeger
from .common_constants import REGEX_MARK, BASE_PATH_MARK, EMPTY


def generate_by_regex(template):
    if isinstance(template, str) and template.startswith(REGEX_MARK):
        template = xeger(template.replace(REGEX_MARK, EMPTY))
    return template


def get_base_path(template, connections):
    if isinstance(template, str) and template.startswith(BASE_PATH_MARK):
        template = connections.clients_bus[template.replace(BASE_PATH_MARK, EMPTY)].base_url
    return template


def single_regex_find(text, regex):
    try:
        return re.findall(regex, text).pop()
    except IndexError as e:
        return None


def single_regex_find_non_none(text, regex, not_found_msg):
    try:
        return re.findall(regex, text).pop()
    except IndexError as e:
        raise Exception(not_found_msg)


def substr(text: str, regex: str, group: int = 0):
    result = re.search(pattern=regex, string=text)
    if result is not None:
        try:
            return result.group(group)
        except IndexError:
            raise Exception(f'No group in the result [ {group} ]!')
    raise Exception(f'There are no substrings in the text \n'
                    f'that match the regular expression: {regex}')
