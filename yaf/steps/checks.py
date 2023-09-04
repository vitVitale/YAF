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
    @allure.step('Check value of response field')
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
                assert re.match(f'{expected_val}', actual_val), f'The value in the field <{render_tags_obj}> ' \
                                                                f'does not match the regular expression!!\n' \
                                                                f'   regex: {expected_val} \n' \
                                                                f'  actual: {actual_val}'
            else:
                assert expected_val == actual_val, f'Values in field <{render_tags_obj}> are not equal !!\n' \
                                                   f'expected[{type(expected_val)}]: {expected_val} \n' \
                                                   f'  actual[{type(actual_val)}]: {actual_val}'

        if isinstance(rendered_value, list) and not isinstance(expected, list):
            for item in rendered_value:
                checker(actual_val=item, expected_val=expected)
        else:
            checker(actual_val=rendered_value, expected_val=expected)

        info_mess = "SUCCESS => Values match !\n"
        allure.attach(f'field:  \t[ {render_tags_obj} ] \n'
                      f'expected: \t[ {expected} ] \n'
                      f'actual: \t[ {rendered_value} ]', info_mess, allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Check multiple response fields')
    def check_several_values_to_expected(target_list, expected_list):
        is_fail = False
        fails_summary = '\n'
        assert len(target_list) == len(expected_list), f'Collections of different sizes, verification is not possible!!'
        for i in range(len(target_list)):
            try:
                AssertSteps.check_value_match_to_expected(target_list[i], expected_list[i])
            except AssertionError as aex:
                is_fail = True
                fails_summary += f'\n{aex}\n'
        assert not is_fail, fails_summary

    @staticmethod
    @allure.step('Check that elements are in the list')
    def check_list_values_to_expected(tags_obj, expected):

        # TODO :: add other options !
        #  expected: 'EACH_CONTAINS_IN_>> '
        #  expected: 'AT_LEAST_ONE_CONTAINS_IN_>> '

        check_type = expected.split('_>> ')[0]
        target_list = AssertSteps.render_template(raw_plate=tags_obj, is_hard_replaced=True)
        expected = AssertSteps.perform_replacement_and_return(text=expected.split('_>> ')[1])
        assert isinstance(target_list, list), 'The passed object is not a list !!'

        if check_type == 'EACH_CONTAINS_IN':
            message = f'whitelist: \t{expected} \n' \
                      f'   target: \t{target_list}'
            assert isinstance(expected, list), 'The validating object is not a list !!'
            assert all(i in expected for i in target_list), f'Not all elements are in the validating list !!\n' \
                                                            f'{message}'
        else:
            raise Exception(f'Unknown validation type {check_type} !!')

        info_mess = "SUCCESS => \n"
        allure.attach(f'check_type: \t{check_type} \n'
                      f'{message}', info_mess, allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Check presence/absence of element in response')
    def check_value_not_match_to_expected(tags_obj, expected: bool):
        is_exist = True
        try:
            AssertSteps.render_template(raw_plate=tags_obj, is_hard_replaced=True)
        except AssertionError:
            is_exist = False
        assert expected == is_exist, f"For element [{tags_obj}]\n" \
                                     f"  Actual state: {is_exist}\n" \
                                     f"Expected state: {expected}"

    @staticmethod
    @allure.step('Check presence/absence of multiple elements in response')
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
    @allure.step('Validate response with JSON schema')
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
            raise AssertionError(f'(Validation error)\n\n{ex}')

    @staticmethod
    @allure.step('Compare values of two response fields with dates')
    def check_values_by_two_dates(tags_obj1, tags_obj2):
        value1 = AssertSteps.render_template(raw_plate=tags_obj1, is_hard_replaced=False)
        value2 = AssertSteps.render_template(raw_plate=tags_obj2, is_hard_replaced=True)

        # a crutch for converting a timestamp from a redis (if that's the format), parser can't handle it
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

        assert value1 == value2, f'Values do not match !!\n' \
                                 f'value1: {value1} \n' \
                                 f'value2: {value2}'

        info_mess = "SUCCESS => Values match !\n"
        allure.attach(f'value1: \t[ {value1} ] \n'
                      f'value2: \t[ {value2} ]', info_mess, allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Check Prometheus metrics')
    def check_prometheus_metrics(instance, metrics_list, expected_list):
        msg = tabulate(tabular_data=dict(zip(metrics_list, [str(i) for i in expected_list])).items(),
                       headers=['Metric_name', 'Expected_value'], tablefmt='grid')
        allure.attach(msg, 'Expect - \n', allure.attachment_type.TEXT)
        client = AssertSteps.connections.get_client(instance)
        response = client.exchange('GET', f'{client.base_url}/actuator/prometheus', None, None)
        assert len(metrics_list) == len(expected_list), f'Collections of metrics and expected values of different sizes'
        assert 200 == response.status_code, f'Failed to get metrics for {instance} !!'
        metrics = response.text
        is_fail = False
        fails_summary = '\n'
        for i in range(len(metrics_list)):
            try:
                catch = single_regex_find(text=metrics, regex=f'{metrics_list[i]} (.+)')
                catch = float(catch) if catch is not None else catch
                assert expected_list[i] == catch, f'Metric value [{metrics_list[i]}] \n' \
                                                  f'expected: {expected_list[i]} \n' \
                                                  f'  actual: {catch}'
            except AssertionError as aex:
                is_fail = True
                fails_summary += f'\n{aex}\n'
        assert not is_fail, fails_summary
