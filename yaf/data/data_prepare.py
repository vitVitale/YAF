import re
import os
import yaml
import pandas as pd
from ast import literal_eval
from yaf.utils.common_constants import FEATURES_DIR, RESOURCES_DIR, TEST_MODEL


class CollectedTests:
    def __init__(self):
        global TEST_MODEL
        if TEST_MODEL is None:
            raise Exception("env.TEST_MODEL не задан!")

        self.test_set = []
        self.preset_teardown = {}
        self.config_set = set()

        if TEST_MODEL == 'ALL':
            watcher = (next(os.walk(f'{FEATURES_DIR}'), (None, [], [])))
            dirs_and_files = watcher[1] + watcher[2]
            TEST_MODEL = ','.join(dirs_and_files)

        for feature in TEST_MODEL.split(','):
            if os.path.isdir(f'{FEATURES_DIR}/{feature}'):
                for inner_feature in next(os.walk(f'{FEATURES_DIR}/{feature}'), (None, None, []))[2]:
                    self._parse_tests(f'{feature}/{inner_feature}')
            else:
                self._parse_tests(feature)

    def _parse_tests(self, file_name):
        with open(f'{FEATURES_DIR}/{file_name}', "r", encoding='utf-8') as stream:
            try:
                self.tests_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise Exception(f'Не удалось распарсить файл {file_name} \n{exc.__cause__}')

        self.feature = self.tests_dict['feature']
        self.epic = self.tests_dict['epic']
        self.preset_teardown[self.feature] = CollectedTests._setup(type_of_setup='once', tests=self.tests_dict)
        before_and_after_each = CollectedTests._setup(type_of_setup='each', tests=self.tests_dict)
        before_and_after_only = CollectedTests._setup(type_of_setup='only', tests=self.tests_dict)
        self.config_set.update(self.tests_dict.get('setup', {}).get('context', {}).get('required', []))
        for test in self.tests_dict['tests']:
            preset, teardown = CollectedTests._setup_applier(instance=test,
                                                             default_set=before_and_after_each,
                                                             custom_set=before_and_after_only)
            test['before'] = preset
            test['after'] = teardown
            test['feature'] = self.feature
            test['epic'] = self.epic
            if not any((key in test) for key in ['test_data_from_csv', 'test_data']):
                self.test_set.append(test)
            else:
                if 'test_data' in test:
                    test_data = test.pop('test_data', None)
                else:
                    td_csv: dict = test.pop('test_data_from_csv', None)
                    df = pd.read_csv(f'{RESOURCES_DIR}/{td_csv["file"]}', sep=td_csv['delimiter'])
                    test_data = df.to_dict(orient='records')[td_csv.get('from'):td_csv.get('to')]
                test_raw = test
                index = 1
                for param_row in test_data:
                    test_instance = test_raw.copy()
                    test_instance['name'] = f'{test_instance["name"]} <{index}>'
                    test_instance['params'] = param_row
                    test_instance = str(test_instance)
                    for param in param_row:
                        test_instance = test_instance.replace(f'{{{{ {param} }}}}', param_row[param]
                                                              .replace("'", "\\'").replace('"', '\\"'))
                    self.test_set.append(literal_eval(test_instance))
                    index += 1

            for step in test['steps']:
                s = step['command']
                if re.match('.*-\\w', s):
                    self.config_set.add(re.sub(r'.*-', '', step['command']))

    @staticmethod
    def _setup(type_of_setup, tests):
        before_after = [None, None]
        if 'setup' in tests:
            if type_of_setup in tests['setup']:
                setup_block = tests['setup'][type_of_setup]
                before_after = []
                if isinstance(setup_block, dict):
                    for instruction in ['before', 'after']:
                        try:
                            before_after.append(setup_block[instruction])
                        except:
                            print(f'Отсутствует блок инструкции [ {instruction} ] !!')
                            before_after.append(None)
                elif isinstance(setup_block, list):
                    return setup_block

        return tuple(before_after)

    @staticmethod
    def _setup_applier(instance, default_set, custom_set):
        if isinstance(custom_set, list) and 'tags' in instance:
            before, after = [], []
            for tag in instance['tags']:
                for setup_instr in custom_set:
                    if tag in setup_instr['tags']:
                        before.extend(setup_instr.get('before', []))
                        after.extend(setup_instr.get('after', []))

            if before or after:
                return before, after

        return default_set[0], default_set[1]
