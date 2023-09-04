from .wsocket import WSocketSteps
from .graphql import GraphQLSteps
from .thrift import ThriftSteps
from .grpc import GrpcSteps
from .rest import RestSteps
from .kafka import KafkaSteps
from .cache import CacheSteps
from .redis import RedisSteps
from .mongo import MongoSteps
from .sql_db import SqlSteps
from .elastic import ElkSteps
from .checks import AssertSteps
from .commons import CommonSteps
from .docker import DockerSteps
from .files import FilesSteps


class BaseContext(KafkaSteps,
                  MongoSteps,
                  CacheSteps,
                  RedisSteps,
                  ElkSteps,
                  SqlSteps,
                  RestSteps,
                  WSocketSteps,
                  GraphQLSteps,
                  ThriftSteps,
                  GrpcSteps,
                  CommonSteps,
                  DockerSteps,
                  FilesSteps,
                  AssertSteps):

    register = {
        # Kafka section
        'send_byte_arr_to_kafka':               'Send byte array to Kafka-.+',
        'send_extended_msg_to_kafka':           'Send extended message to Kafka-.+',
        'send_message_to_kafka':                'Send message to Kafka-.+',
        'find_message_kafka':                   'Find message from Kafka-.+',
        'find_msg_with_timeout_kafka':          'Find message with timeout from Kafka-.+',
        'get_last_message_kafka':               'Get the last record from Kafka-.+',
        # Rest section
        'send_rest_request':                    'Send request REST-.+',
        'send_async_rest_request':              'Send asynchronous request REST-.+',
        'get_async_rest_response':              'Get asynchronous response REST-.+',
        # GraphQL section
        'send_graphql_request':                 'Send request GraphQL-.+',
        # Thrift section
        'send_thrift_request':                  'Send request THRIFT-.+',
        # gRPC section
        'send_grpc_request':                    'Send request GRPC-.+',
        'send_json_like_grpc_request':          'Send json request GRPC-.+',
        # WebSocket section
        'ws_create_connection':                 'Launch client WebSocket-.+',
        'receive_from_ws':                      'Receive from WebSocket-.+',
        'send_event_to_ws':                     'Send event to WebSocket-.+',
        # Cache section
        'create_cache_scheme':                  'Create schema in Cache-.+',
        'delete_cache_scheme':                  'Delete schema in Cache-.+',
        'put_into_cache':                       'Write value into Cache-.+',
        'get_from_cache':                       'Get value from Cache-.+',
        'delete_from_cache':                    'Delete from Cache-.+',
        # Redis section
        'put_into_redis':                       'Write value into Redis-.+',
        'get_from_redis':                       'Get value from Redis-.+',
        'get_keys_in_redis':                    'Get keys by pattern from Redis-.+',
        # Mongo DB section
        'find_data_in_mongo':                   'Find objects in MongoDB-.+',
        'remove_data_from_mongo':               'Remove objects in MongoDB-.+',
        'insert_data_into_mongo':               'Insert objects into MongoDB-.+',
        'update_data_into_mongo':               'Update objects in MongoDB-.+',
        # SQL DB section
        'exec_change_query_db':                 'Execute changing request in DB-.+',
        'exec_search_query_db':                 'Execute searching request in DB-.+',
        # Elasticsearch section
        'get_doc_from_elk':                     'Get document from Elasticsearch-.+',
        'get_doc_from_elk_by_index_and_query':  'Get document from Elasticsearch by index and content-.+',
        'search_docks_in_elk':                  'Search documents in Elasticsearch-.+',
        'extended_search_docks_in_elk':         'Advanced search documents in Elasticsearch-.+',
        # Commons section
        'execute_shell':                        'Execute Bash script',
        'execute_remote_cmd':                   'Execute commands via SSH-.+',
        'download_file_by_sftp':                'Download file via SFTP-.+',
        'execute_liquibase_task':               'Execute Liquibase Task for DB-.+',
        'save_to_test_scope_var':               'Save value to variable',
        'delay_wait_in_mills':                  'Explicit wait in milliseconds',
        'generate_json_web_token':              'Generate JWT token',
        # Checks section
        'validate_by_json_scheme':              'Validate response with JSON schema-.+',
        'check_value_match_to_expected':        'Check value of response field',
        'check_several_values_to_expected':     'Check multiple response fields',
        'check_list_values_to_expected':        'Check that elements are in the list',
        'check_values_by_two_dates':            'Compare values of two response fields with dates',
        'check_sql_result_with_expected':       'Check SQL response values-.+',
        'check_value_not_match_to_expected':    'Check presence/absence of element in response',
        'check_existence_of_several_values':    'Check presence/absence of multiple elements in response',
        'check_prometheus_metrics':             'Check Prometheus metrics for-.+',
        # Files section
        'edit_yml_file':                        'Edit YAML file-.+',
        'edit_json_file':                       'Edit JSON file-.+',
        # Docker section
        'control_st_environment':               'Control ST environment'
    }

