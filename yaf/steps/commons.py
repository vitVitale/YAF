import re
import os
import jwt
import allure
import subprocess
from time import sleep
from .base_operations import Base
from yaf.utils.common_constants import RESOURCES_DIR, REGEX_MARK, EMPTY, PATH_COMPENSATOR, ENV_FILE_NAME
from yaf.data.parsers.liquibase_command_extractor import parse
from yaf.data.parsers.jwt_command_extractor import jwt_parse
from yaf.steps.files import FilesSteps


class CommonSteps(Base):

    @staticmethod
    @allure.step('Execute Bash script')
    def execute_shell(text, expected):
        text = CommonSteps.render_and_attach(text)
        result = subprocess.run(text, cwd='../',
                                capture_output=True,
                                check=True, shell=True)
        result = f'STDOUT:\n{result.stdout.decode("utf-8")}\n' \
                 f'STDERR:\n{result.stderr.decode("utf-8")}'
        save_flag = 'SAVE' == expected.upper()
        info_mess = 'Received console log - \n'
        CommonSteps.attach_request_block(info_mess=info_mess,
                                         save=save_flag,
                                         body=result)

    @staticmethod
    @allure.step('Execute Liquibase Task for DataBase')
    def execute_liquibase_task(client_name, text):
        client = CommonSteps.connections.get_client(client_name)
        parsed_dict = parse(CommonSteps.render_and_attach(text))
        request = f"""
        liquibase-4.7.1/liquibase{f' --contexts="{parsed_dict["contexts"]}"' if parsed_dict["contexts"] else ''} \\
         --driver={CommonSteps._driver(client.config)} \\
         --classpath={CommonSteps._classpath(client.config)} \\
         --changeLogFile="db/{parsed_dict['changelog']}" \\
         --url="{CommonSteps._jdbc_url(client_conf=client.config, 
                                       schema=parsed_dict['schema'])}" \\
         --username={client.config['username']} \\
         --password={client.config['password']} \\
        {parsed_dict['task']}
        """.strip()
        result = subprocess.run(request, cwd=f'{PATH_COMPENSATOR}migrations_tools',
                                capture_output=True,
                                check=True, shell=True).stderr.decode("utf-8")
        CommonSteps.attach_request_block(info_mess='Liquibase log - \n',
                                         body=result,
                                         save=False)

    @staticmethod
    @allure.step('Execute commands via SSH')
    def execute_remote_cmd(client_name, text, expected=None):
        client = CommonSteps.connections.get_client(client_name)
        text = CommonSteps.render_and_attach(text)
        result = client.execute_cmd(commands=text)

        if expected is not None:

            if expected.startswith(REGEX_MARK):
                expected = expected.replace(REGEX_MARK, EMPTY)
                assert re.match(f'{expected}', result), f'The value in the field <{result}> does not match' \
                                                        f' the regular expression!!\n' \
                                                        f'   regex: {expected} \n' \
                                                        f'  actual: {result}'
            else:

                assert result == expected, f'result is not equal to expected !!\n' \
                                           f'expected: {expected} \n' \
                                           f'  actual: {result}'

        info_mess = 'Received console log - \n'
        allure.attach(result, info_mess, allure.attachment_type.TEXT)
        CommonSteps.put_response_to_stash(result)

    @staticmethod
    @allure.step('Download file via SFTP')
    def download_file_by_sftp(client_name, remote_filepath):
        client = CommonSteps.connections.get_client(client_name)
        remote_filepath = CommonSteps.render_and_attach(remote_filepath)
        client.download_file(remote_file=remote_filepath)
        path = f"{RESOURCES_DIR}/{remote_filepath[remote_filepath.rfind('/')+1:]}"
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as file:
                path = file.read()
        info_mess = 'Received file - \n'
        CommonSteps.attach_response_block(info_mess=info_mess,
                                          body=path)

    @staticmethod
    @allure.step('Explicit wait in milliseconds')
    def delay_wait_in_mills(text):
        sleep(float(text)/1000)

    @staticmethod
    @allure.step('Save value to variable')
    def save_to_test_scope_var(text, var_name):
        var = CommonSteps.render_and_attach(text)
        if not isinstance(var_name, dict):
            CommonSteps.stash[f'env.{var_name}'] = var
            return
        if not var_name.get('scope') == 'env_file':
            CommonSteps.stash[f"{var_name['scope']}.{var_name['name']}"] = var
            return
        FilesSteps.check_if_is_file_exist_and_create_if_not(ENV_FILE_NAME)
        FilesSteps.edit_yml_file(file_name=ENV_FILE_NAME,
                                 paths=[var_name['name']],
                                 new_values=[var])

    @staticmethod
    @allure.step('Generate JWT token')
    def generate_json_web_token(text, var_name):
        parsed_dict = jwt_parse(CommonSteps.render_and_attach(text))
        token = jwt.encode(algorithm=parsed_dict['algorithm'],
                           payload=parsed_dict['data'],
                           key=parsed_dict['key'])
        info_mess = 'Received token - \n'
        allure.attach(token, info_mess, allure.attachment_type.TEXT)
        CommonSteps.stash[f'env.{var_name}'] = token

########################################################################################################################

    @staticmethod
    def _jdbc_url(client_conf, schema=None):
        template = None
        if 'postgresql' == client_conf['drivername']:
            template = f'jdbc:postgresql://' \
                       f'{client_conf["host"]}:' \
                       f'{client_conf["port"]}/' \
                       f'{client_conf["database"]}?currentSchema={schema}'
        elif 'oracle' == client_conf['drivername']:
            template = f'jdbc:oracle:thin:@' \
                       f'{client_conf["host"]}:' \
                       f'{client_conf["port"]}:' \
                       f'{client_conf["database"]}'
        return template

    @staticmethod
    def _driver(client_conf):
        if 'postgresql' == client_conf['drivername']:
            return 'org.postgresql.Driver'
        elif 'oracle' == client_conf['drivername']:
            return 'oracle.jdbc.driver.OracleDriver'

    @staticmethod
    def _classpath(client_conf):
        if 'postgresql' == client_conf['drivername']:
            return 'postgresql-42.2.8.jar'
        elif 'oracle' == client_conf['drivername']:
            return 'liquibase-4.7.1/lib/ojdbc8-18.3.0.0.jar'
