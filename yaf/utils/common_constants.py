import os
from typing import final


def get_counter(var):
    if var:
        if str(var).isnumeric():
            if int(var) in range(6):
                return int(var)
    return 0


# System paths & variables
PATH_COMPENSATOR: final(str) = os.getenv('PATH_COMPENSATOR', default='../../')
API_CONTEXT: final(str) = os.getcwd()+f'/{PATH_COMPENSATOR}test_model/api_context.yml'
FEATURES_DIR: final(str) = os.getcwd()+f'/{PATH_COMPENSATOR}test_model/features'
RESOURCES_DIR: final(str) = os.getcwd()+f'/{PATH_COMPENSATOR}test_model/resources'
SECRETS_DIR: final(str) = os.getcwd()+f'/{PATH_COMPENSATOR}test_model/secrets'
THRIFT_DIR: final(str) = os.getcwd()+f'/{PATH_COMPENSATOR}test_model/thrift'
GRPC_DIR: final(str) = os.getcwd()+f'/{PATH_COMPENSATOR}test_model/grpc'
TEST_MODEL: final(str) = os.environ.get('TEST_MODEL')
CUSTOM_CTX: final(str) = os.environ.get('CUSTOM_CTX')
DECRYPT_KEY: final(str) = os.environ.get('DECRYPT_KEY')
RERUN_COUNTER: final(int) = get_counter(os.environ.get('FLAKY_RERUN'))
ENV_FILE_NAME: final(str) = '__env_file__.yml'
ENV_FILE: final(str) = f'{RESOURCES_DIR}/{ENV_FILE_NAME}'


# DSL & other tags
EMPTY: final(str) = ''
REGEX_MARK: final(str) = 'REGEX '
JPATH_MARK: final(str) = 'JPATH '
STRUCT_MARK: final(str) = 'STRUCT '
GET_FILE_MARK: final(str) = 'GET_FILE '
TEST_DATA: final(str) = '<__TEST_DATA__>'
BASE_PATH_MARK: final(str) = 'BASE_PATH '
HTTP_CODE: final(str) = 'HTTP CODE: '
SQL_MARK: final(str) = '(\[){0,1}SQL_RS_\d+ .+'
HEADERS_MARK: final(str) = '(HEADERS_RS_\d+) : (.+)'
ENCRYPTED_MARK: final(str) = r'<\[ ENCRYPTED ]>( ){0,1}(.+)'
JIRA_PATH: final(str) = 'https://jira.your_server.com/secure/Tests.jspa#/testCase'
