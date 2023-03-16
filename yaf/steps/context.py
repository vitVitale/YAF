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
        'send_byte_arr_to_kafka':               'Отправить массив байт в Kafka-.+',
        'send_extended_msg_to_kafka':           'Отправить расширенный запрос в Kafka-.+',
        'send_message_to_kafka':                'Отправить запрос в Kafka-.+',
        'find_message_kafka':                   'Получить запрос из Kafka-.+',
        'find_msg_with_timeout_kafka':          'Получить запрос с таймаутом из Kafka-.+',
        'get_last_message_kafka':               'Получить последнюю запись из Kafka-.+',
        # Rest section
        'send_rest_request':                    'Отправить запрос REST-.+',
        'send_async_rest_request':              'Отправить асинхронный запрос REST-.+',
        'get_async_rest_response':              'Получить ответ на асинхронный запрос REST-.+',
        # GraphQL section
        'send_graphql_request':                 'Отправить запрос GraphQL-.+',
        # Thrift section
        'send_thrift_request':                  'Отправить запрос THRIFT-.+',
        # gRPC section
        'send_grpc_request':                    'Отправить запрос GRPC-.+',
        'send_json_like_grpc_request':          'Отправить json запрос GRPC-.+',
        # WebSocket section
        'ws_create_connection':                 'Запустить клиент WebSocket-.+',
        'receive_from_ws':                      'Получить ответ WebSocket-.+',
        'send_event_to_ws':                     'Отправить запрос WebSocket-.+',
        # Cache section
        'create_cache_scheme':                  'Создать схему в Cache-.+',
        'delete_cache_scheme':                  'Удалить схему в Cache-.+',
        'put_into_cache':                       'Записать значение в Cache-.+',
        'get_from_cache':                       'Получить значение из Cache-.+',
        'delete_from_cache':                    'Удалить из Cache-.+',
        # Redis section
        'put_into_redis':                       'Записать значение в Redis-.+',
        'get_from_redis':                       'Получить значение из Redis-.+',
        'get_keys_in_redis':                    'Получить ключи по шаблону из Redis-.+',
        # Mongo DB section
        'find_data_in_mongo':                   'Поиск объектов в MongoDB-.+',
        'remove_data_from_mongo':               'Удалить объект\(ы\) в MongoDB-.+',
        'insert_data_into_mongo':               'Записать объект\(ы\) в MongoDB-.+',
        'update_data_into_mongo':               'Обновить объект\(ы\) в MongoDB-.+',
        # SQL DB section
        'exec_change_query_db':                 'Выполнить запрос на изменение в БД-.+',
        'exec_search_query_db':                 'Выполнить поисковый запрос в БД-.+',
        # Elasticsearch section
        'get_doc_from_elk':                     'Получить документ из Elasticsearch-.+',
        'get_doc_from_elk_by_index_and_query':  'Получить документ из Elasticsearch по индексу и содержимому-.+',
        'search_docks_in_elk':                  'Поиск документов в Elasticsearch-.+',
        'extended_search_docks_in_elk':         'Расширенный поиск документов в Elasticsearch-.+',
        # Commons section
        'execute_shell':                        'Выполнить Bash скрипт',
        'execute_remote_cmd':                   'Выполнить команды по SSH-.+',
        'download_file_by_sftp':                'Скачать файл по SFTP-.+',
        'execute_liquibase_task':               'Выполнить Liquibase Task для БД-.+',
        'save_to_test_scope_var':               'Сохранить значение в переменную',
        'delay_wait_in_mills':                  'Явное ожидание в миллисекундах',
        'generate_json_web_token':              'Сгенерировать JWT token',
        # Checks section
        'validate_by_json_scheme':              'Проверяем схемой ответ-.+',
        'check_value_match_to_expected':        'Проверяем значение поля ответа',
        'check_several_values_to_expected':     'Проверяем несколько полей ответа',
        'check_list_values_to_expected':        'Проверяем что элементы в списке',
        'check_values_by_two_dates':            'Сравниваем значения полей двух ответов с датами',
        'check_sql_result_with_expected':       'Проверяем значения SQL ответа-.+',
        'check_value_not_match_to_expected':    'Проверка наличия/отсутствия элемента в ответе',
        'check_existence_of_several_values':    'Проверка наличия/отсутствия нескольких элементов в ответе',
        'check_prometheus_metrics':             'Проверка Prometheus метрик для-.+',
        # Files section
        'edit_yml_file':                        'Редактировать YAML файл-.+',
        'edit_json_file':                       'Редактировать JSON файл-.+',
        # Docker section
        'control_st_environment':               'Управлять ST окружением'
    }

