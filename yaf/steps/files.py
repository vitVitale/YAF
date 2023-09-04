import yaml
import allure
from enum import Enum
from pathlib import Path
from json import dumps, loads
from jsonpath_ng.ext import parse
from tabulate import tabulate
from .base_operations import Base
from yaf.utils.common_constants import RESOURCES_DIR


class DocType(Enum):
    JSON = allure.attachment_type.JSON
    YAML = allure.attachment_type.YAML


class FilesSteps(Base):

    @staticmethod
    @allure.step('Edit YAML file')
    def edit_yml_file(file_name, paths, new_values):
        FilesSteps._edit_file(doctype=DocType.YAML,
                              file_name=file_name,
                              values=new_values,
                              paths=paths)

    @staticmethod
    @allure.step('Edit JSON file')
    def edit_json_file(file_name, paths, new_values):
        FilesSteps._edit_file(doctype=DocType.JSON,
                              file_name=file_name,
                              values=new_values,
                              paths=paths)

########################################################################################################################

    @staticmethod
    def check_if_is_file_exist_and_create_if_not(file_name: str):
        file = Path(f"{RESOURCES_DIR}/{file_name}")
        file.touch(exist_ok=True)

    @staticmethod
    def _edit_file(doctype: DocType, file_name: str, paths: list, values: list):
        assert len(paths) == len(values), 'Different data dimensions!'
        doc: dict = FilesSteps._read_file(file_name, doctype.name, doctype.value)
        FilesSteps._apply_changes(doc, paths, values)
        FilesSteps._write_file(doc, file_name, doctype.name, doctype.value)

    @staticmethod
    def _read_file(file_name: str, types: str, attach_type):
        types = types.upper()
        with open(f'{RESOURCES_DIR}/{file_name}', "r", encoding='utf-8') as stream:
            text = stream.read()
            allure.attach(text, 'initial file - \n', attach_type)
            try:
                if 'JSON' == types:
                    result_map = loads(text)
                elif 'YAML' == types:
                    result_map = yaml.safe_load(text)
                else:
                    raise Exception(f'File type [{types}] is not supported!')
            except Exception as exc:
                raise Exception(f'Failed to parse file\n{exc}')
            return result_map if result_map else {}

    @staticmethod
    def _apply_changes(obj_dict: dict, paths: list, new_values: list):
        changes = []
        for i in range(len(paths)):
            jpath = parse(f'$.{paths[i]}')
            results = [x.value for x in jpath.find(obj_dict)]
            match len(results):
                case 0:
                    old_values = None
                    obj_dict[paths[i]] = new_values[i]
                case 1: old_values = results[0]
                case _: old_values = results
            jpath.update(obj_dict, new_values[i])
            changes.append((paths[i], old_values, new_values[i]))

        changes = tabulate(headers=['Path', 'Old Value', 'New Value'],
                           tabular_data=changes,
                           tablefmt='grid')
        allure.attach(changes, 'changeset - \n', allure.attachment_type.TEXT)

    @staticmethod
    def _write_file(obj_dict: dict, file_name: str, types: str, attach_type):
        types = types.upper()
        with open(f'{RESOURCES_DIR}/{file_name}', "w", encoding='utf-8')as f:
            if 'JSON' == types:
                refreshed = dumps(obj_dict, indent=2, ensure_ascii=False)
            elif 'YAML' == types:
                refreshed = yaml.safe_dump(obj_dict, default_flow_style=False,
                                           allow_unicode=True, sort_keys=False)
            else:
                raise Exception(f'File type [{types}] is not supported!')
            f.write(refreshed)
        allure.attach(refreshed, 'updated file - \n', attach_type)
