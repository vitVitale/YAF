import pytz
import dateutil.parser as parser
import datetime
import re
import allure
from json import loads
from tabulate import tabulate
from jsonschema import validate, ValidationError
from .base_operations import Base
from yaf.utils.common_constants import REGEX_MARK, EMPTY
from yaf.utils.regex_operations import single_regex_find


class AssertSteps(Base):

    @staticmethod
    @allure.step('Проверяем значение поля ответа')
    def check_value_match_to_expected(tags_obj, expected):
        tags_obj = AssertSteps.perform_replacement_and_return(tags_obj)
        if isinstance(expected, str):
            expected = AssertSteps.perform_replacement_and_return(expected)
        try:
            render_tags_obj = tags_obj.split(' : ')[2]
        except IndexError:
            render_tags_obj = tags_obj
        rendered_value = AssertSteps.render_template(raw_plate=tags_obj, is_hard_replaced=True)
        expected = AssertSteps.render_template(raw_plate=expected, is_hard_replaced=False)

        def checker(actual_val, expected_val):
            if isinstance(expected_val, str) and expected_val.startswith(REGEX_MARK):
                actual_val = str(actual_val)
                expected_val = expected_val.replace(REGEX_MARK, EMPTY)
                assert re.match(f'{expected_val}', actual_val), f'Значения в поле <{render_tags_obj}> не соответсвует' \
                                                                f' регулярному выражению!!\n' \
                                                                f'   regex: {expected_val} \n' \
                                                                f'  actual: {actual_val}'
            else:
                assert expected_val == actual_val, f'Значения в поле <{render_tags_obj}> не равно !!\n' \
                                                   f'expected[{type(expected_val)}]: {expected_val} \n' \
                                                   f'  actual[{type(actual_val)}]: {actual_val}'

        if isinstance(rendered_value, list) and not isinstance(expected, list):
            for item in rendered_value:
                checker(actual_val=item, expected_val=expected)
        else:
            checker(actual_val=rendered_value, expected_val=expected)

        info_mess = "SUCCESS => Значения совпадают !\n"
        allure.attach(f'field:  \t[ {render_tags_obj} ] \n'
                      f'expected: \t[ {expected} ] \n'
                      f'actual: \t[ {rendered_value} ]', info_mess, allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Проверяем несколько полей ответа')
    def check_several_values_to_expected(target_list, expected_list):
        is_fail = False
        fails_summary = '\n'
        assert len(target_list) == len(expected_list), f'Коллекции разного размера, проверка не возможна!!'
        for i in range(len(target_list)):
            try:
                AssertSteps.check_value_match_to_expected(target_list[i], expected_list[i])
            except AssertionError as aex:
                is_fail = True
                fails_summary += f'\n{aex}\n'
        assert not is_fail, fails_summary

    @staticmethod
    @allure.step('Проверяем что элементы в списке')
    def check_list_values_to_expected(tags_obj, expected):

        # TODO :: добавить другие опции !
        #  expected: 'EACH_CONTAINS_IN_>> '
        #  expected: 'AT_LEAST_ONE_CONTAINS_IN_>> '

        check_type = expected.split('_>> ')[0]
        target_list = AssertSteps.render_template(raw_plate=tags_obj, is_hard_replaced=True)
        expected = AssertSteps.perform_replacement_and_return(text=expected.split('_>> ')[1])
        assert isinstance(target_list, list), 'Переданный объект не является списком !!'

        if check_type == 'EACH_CONTAINS_IN':
            message = f'whitelist: \t{expected} \n' \
                      f'   target: \t{target_list}'
            assert isinstance(expected, list), 'Валидирующий объект не является списком !!'
            assert all(i in expected for i in target_list), f'Не все элементы содержатся в валидирующем списке !!\n' \
                                                            f'{message}'
        else:
            raise Exception(f'Неизвестный тип проверки {check_type} !!')

        info_mess = "SUCCESS => \n"
        allure.attach(f'check_type: \t{check_type} \n'
                      f'{message}', info_mess, allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Проверка наличия элемента в ответе')
    def check_value_not_match_to_expected(tags_obj, expected: bool):
        is_exist = True
        try:
            AssertSteps.render_template(raw_plate=tags_obj, is_hard_replaced=True)
        except AssertionError:
            is_exist = False
        assert expected == is_exist, f"Для элемента [{tags_obj}]\n" \
                                     f"Актуальное состояние: {is_exist}\n" \
                                     f"Ожидаемое состояние: {expected}"

    @staticmethod
    @allure.step('Проверка наличия/отсутствия нескольких элементов в ответе')
    def check_existence_of_several_values(args):
        is_fail = False
        fails_summary = '\n'
        for row in args:
            try:
                AssertSteps.check_value_not_match_to_expected(row['target'], row['expected'])
            except AssertionError as aex:
                is_fail = True
                fails_summary += f'\n{aex}\n'
        assert not is_fail, fails_summary

    @staticmethod
    @allure.step('Валидируем документ JSON схемой')
    def validate_by_json_scheme(json_doc, json_schema):
        json_doc = AssertSteps.stash[json_doc]
        json_schema = AssertSteps.perform_replacement_and_return(json_schema)
        info_mess = 'VALIDATION SCHEMA :\n'
        allure.attach(json_schema,
                      info_mess,
                      allure.attachment_type.JSON)
        try:
            validate(instance=loads(json_doc),
                     schema=loads(json_schema))
        except ValidationError as ex:
            raise AssertionError(f'(Ошибка валидации)\n\n{ex}')

    @staticmethod
    @allure.step('Сравниваем значения полей двух ответов с датами')
    def check_values_by_two_dates(tags_obj1, tags_obj2):
        value1 = AssertSteps.render_template(raw_plate=tags_obj1, is_hard_replaced=False)
        value2 = AssertSteps.render_template(raw_plate=tags_obj2, is_hard_replaced=True)

        # костыль для преобразования timestamp из редиса(если таков формат), parser с ним обращаться не умеет
        try:
            value1 = parser.parse(value1).astimezone(pytz.utc).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
        except OverflowError:
            value1 = datetime.datetime.fromtimestamp(int(value1) / 1000, tz=pytz.utc).strftime(
                '%Y-%m-%d %H:%M:%S')

        try:
            value2 = parser.parse(value2).astimezone(pytz.utc).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
        except OverflowError:
            value2 = datetime.datetime.fromtimestamp(int(value2) / 1000, tz=pytz.utc).strftime(
                '%Y-%m-%d %H:%M:%S')

        assert value1 == value2, f'Значения не совпадают !!\n' \
                                 f'value1: {value1} \n' \
                                 f'value2: {value2}'

        info_mess = "SUCCESS => Значения совпадают !\n"
        allure.attach(f'value1: \t[ {value1} ] \n'
                      f'value2: \t[ {value2} ]', info_mess, allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Проверка Prometheus метрик')
    def check_prometheus_metrics(instance, metrics_list, expected_list):
        msg = tabulate(tabular_data=dict(zip(metrics_list, [str(i) for i in expected_list])).items(),
                       headers=['Metric_name', 'Expected_value'], tablefmt='grid')
        allure.attach(msg, 'Ожидаем - \n', allure.attachment_type.TEXT)
        client = AssertSteps.connections.get_client(instance)
        response = client.exchange('GET', f'{client.base_url}/actuator/prometheus', None, None)
        assert len(metrics_list) == len(expected_list), f'Коллекции метрик и ожидаемых значений разного размера!!'
        assert 200 == response.status_code, f'Не удалось получить метрики для {instance} !!'
        metrics = response.text
        is_fail = False
        fails_summary = '\n'
        for i in range(len(metrics_list)):
            try:
                catch = single_regex_find(text=metrics, regex=f'{metrics_list[i]} (.+)')
                catch = float(catch) if catch is not None else catch
                assert expected_list[i] == catch, f'Значение метрики [{metrics_list[i]}] \n' \
                                                  f'expected: {expected_list[i]} \n' \
                                                  f'  actual: {catch}'
            except AssertionError as aex:
                is_fail = True
                fails_summary += f'\n{aex}\n'
        assert not is_fail, fails_summary
