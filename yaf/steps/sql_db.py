import re
import allure
from .base_operations import Base
from yaf.fabric.clientTypes.SqlDbClient import ResultSet
from yaf.data.parsers.sql_command_extractor import parse
from yaf.utils.common_constants import REGEX_MARK, EMPTY


class SqlSteps(Base):

    @staticmethod
    @allure.step('Query with changes to DB')
    def exec_change_query_db(client_name, sql, expected):
        sql = SqlSteps.perform_replacement_and_return(text=sql)
        client = SqlSteps.connections.get_client(client_name)
        info_mess = 'SQL request - \n'
        allure.attach(sql, info_mess, allure.attachment_type.TEXT)
        result: bool = client.execute(query=sql)
        info_mess = 'Request completed - \n'
        allure.attach(f'Presence of changes: {str(result)}',
                      info_mess, allure.attachment_type.TEXT)
        if not result:
            flag = 'NO CHANGES ALLOWED' == expected.upper()
            assert flag, 'Expected changes not made !'

    @staticmethod
    @allure.step('Search query to DB with timeout')
    def exec_search_query_db(client_name, sql, expected):
        sql = SqlSteps.perform_replacement_and_return(text=sql)
        client = SqlSteps.connections.get_client(client_name)
        info_mess = 'SQL request - \n'
        allure.attach(sql, info_mess, allure.attachment_type.TEXT)
        result: ResultSet = client.fetch(empty_required=(expected.upper() == 'EMPTY'),
                                         query=sql)
        info_mess = 'Request result - \n'
        allure.attach(result.text_layout, info_mess, allure.attachment_type.TEXT)
        if expected.upper() != 'EMPTY':
            SqlSteps.put_sql_result_to_stash(sql_result=result)

    @staticmethod
    @allure.step('Checking the field value in the SQL response')
    def check_sql_result_with_expected(sql_result, text, expected):
        parsed_dict = parse(SqlSteps.render_and_attach(text))
        answer: ResultSet = SqlSteps.stash[sql_result]
        if parsed_dict['row'] and ('ALL' == parsed_dict['row'].upper()):
            column_values = answer.get_column_values(column=parsed_dict['column'])
            for row in range(len(column_values)):
                SqlSteps.check_values(column_name=parsed_dict['column'],
                                      row_number=row+1,
                                      expected=expected,
                                      actual=column_values[row],
                                      is_list=True)
            allure.attach(f'field:    \t[ {parsed_dict["column"]} ] \n'
                          f'rows:     \t[ {len(column_values)} ] \n'
                          f'expected: \t[ {expected} ]',
                          "SUCCESS => Values match !\n",
                          allure.attachment_type.TEXT)
        else:
            cell_value = str(answer.get_cell_value(column=parsed_dict['column'],
                                                   row=parsed_dict['row']))
            SqlSteps.check_values(column_name=parsed_dict['column'],
                                  row_number=parsed_dict['row'],
                                  expected=expected,
                                  actual=cell_value)

########################################################################################################################

    @staticmethod
    def check_values(actual, expected, column_name, row_number, is_list: bool = False):
        row_number = 1 if row_number is None else row_number
        if expected.startswith(REGEX_MARK):
            expected_clean = expected.replace(REGEX_MARK, EMPTY)
            assert re.match(f'{expected_clean}', actual), f'Values in column <{column_name}> of row <{row_number}>\n' \
                                                          f'Does not match regular expression!!\n' \
                                                          f' regex: {expected_clean} \n' \
                                                          f'actual: {actual}'
        else:
            assert expected == actual, f'Values in column <{column_name}> of row <{row_number}> are not equal !!\n' \
                                       f'expected: {expected} \n' \
                                       f'  actual: {actual}'
        if not is_list:
            SqlSteps._attach_check_result_to_allure(actual, expected, column_name, row_number)

    @staticmethod
    def _attach_check_result_to_allure(actual, expected, column_name, row_number):
        info_mess = "SUCCESS => Values match !\n"
        allure.attach(f'field:    \t[ {column_name} ] \n'
                      f'row:      \t[ {row_number} ] \n'
                      f'expected: \t[ {expected} ] \n'
                      f'actual:   \t[ {actual} ]', info_mess, allure.attachment_type.TEXT)
