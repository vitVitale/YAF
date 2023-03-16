import allure
from yaml import safe_load
from tabulate import tabulate
from .base_operations import Base
from yaf.utils.common_constants import EMPTY
from yaf.fabric.clientTypes.KafkaClient import KafkaRecord, avro_serializer
from yaf.data.parsers.kafka_command_extractor import parse


class KafkaSteps(Base):

    @staticmethod
    @allure.step('Отправить запрос в Kafka')
    def send_message_to_kafka(client_name, payload):
        payload = KafkaSteps.perform_replacement_and_return(payload)
        client = KafkaSteps.connections.get_client(client_name)
        client.send_message(message=payload)
        allure.attach(payload, 'Json отправленный в Kafka -', allure.attachment_type.JSON)
        KafkaSteps.put_request_to_stash(payload)

    @staticmethod
    @allure.step('Отправить расширенный запрос в Kafka')
    def send_extended_msg_to_kafka(client_name, text):
        client = KafkaSteps.connections.get_client(client_name)
        parsed_dict = parse(KafkaSteps.perform_replacement_and_return(text))
        header_tb = '\nHEADERS\n' + tabulate(tabular_data=parsed_dict['headers'].items(),
                                             headers=['Name', 'Value'],
                                             tablefmt='grid') if parsed_dict['headers'] else EMPTY
        additions = f"AVRO_SCHEMA: {parsed_dict['avro_schema']}\n" \
                    f"PARTITION:   {parsed_dict['partition']}\n" \
                    f"TOPIC:       {parsed_dict['topic']}\n" \
                    f"KEY:         {parsed_dict['key']}" \
                    f"{header_tb}"
        allure.attach(additions, 'Дополнения - \n', allure.attachment_type.TEXT)
        msg = avro_serializer(parsed_dict['message'], parsed_dict['avro_schema']) \
            if parsed_dict['avro_schema'] \
            else parsed_dict['message']
        client.send_message(partition=parsed_dict['partition'],
                            headers=parsed_dict['headers'],
                            topic=parsed_dict['topic'],
                            key=parsed_dict['key'],
                            message=msg)
        info_mess = 'Payload отправленный в Kafka - \n'
        KafkaSteps.attach_request_block(body=parsed_dict['message'],
                                        info_mess=info_mess,
                                        save=True)
        if parsed_dict['avro_schema'] is not None:
            info_mess = 'Avro сериализованное сообщение - \n'
            KafkaSteps.attach_request_block(body=str(msg),
                                            info_mess=info_mess,
                                            save=False)

    @staticmethod
    @allure.step('Отправить массив байт в Kafka')
    def send_byte_arr_to_kafka(client_name, text):
        client = KafkaSteps.connections.get_client(client_name)
        topic = safe_load(text)['TOPIC']
        message = safe_load(text)['MESSAGE']
        byte_arr = bytes(message, 'UTF-8')
        client.send_message(topic=topic, message=byte_arr)
        allure.attach(message, 'Сообщение отправленное в Kafka -', allure.attachment_type.TEXT)
        KafkaSteps.put_request_to_stash(message)

    @staticmethod
    @allure.step('Получить последнюю запись из Kafka')
    def get_last_message_kafka(client_name, text):
        client = KafkaSteps.connections.get_client(client_name)
        parsed_dict = parse(KafkaSteps.perform_replacement_and_return(text))
        additions = f"PARTITION:   {parsed_dict['partition']}\n" \
                    f"TOPIC:       {parsed_dict['topic']}\n"
        allure.attach(additions, 'Условия - \n', allure.attachment_type.TEXT)
        record = client.get_last_message_from(partition=parsed_dict['partition'],
                                              topic=parsed_dict['topic'])
        allure.attach(record.value, 'RAW-Payload полученный из Kafka -', allure.attachment_type.TEXT)
        KafkaSteps.put_response_to_stash(body=record)
        KafkaSteps.attach_additions(record)

    @staticmethod
    @allure.step('Получить запрос с таймаутом из Kafka')
    def find_msg_with_timeout_kafka(client_name, text, timeout):
        KafkaSteps.find_msg_kafka(client_name=client_name,
                                  timeout=timeout,
                                  text=text)

    @staticmethod
    @allure.step('Получить запрос из Kafka')
    def find_message_kafka(client_name, text):
        KafkaSteps.find_msg_kafka(client_name=client_name,
                                  text=text)

########################################################################################################################

    @staticmethod
    def find_msg_kafka(client_name, text, timeout=None):
        text = KafkaSteps.render_and_attach(text)
        parsed_dict = parse(text)
        client = KafkaSteps.connections.get_client(client_name)
        record = client.find_message_by_mark(marker=parsed_dict['marker'] if parsed_dict['marker'] else str(text),
                                             time=int(timeout) if timeout else 5,
                                             avsc=parsed_dict['avro_schema'])
        KafkaSteps.attach_response_block(info_mess='Payload полученный из Kafka -', body=record.value)
        KafkaSteps.attach_additions(record)

    @staticmethod
    def attach_additions(record: KafkaRecord):
        key = record.key.decode('utf-8') if record.key else None
        msg = f'PARTITION: {record.partition}\n' \
              f'TOPIC:     {record.topic}\n' \
              f'KEY:       {key}\n'
        if record.headers is not None:
            headers_map = {key: val.decode('utf-8') for (key, val) in record.headers}
            msg = msg + 'HEADERS\n' + tabulate(tabular_data=headers_map.items(),
                                               headers=['Name', 'Value'],
                                               tablefmt='grid')
            KafkaSteps.stash[f'HEADERS_RS_{Base.rsCounter}'] = headers_map
        allure.attach(msg, 'Дополнения - \n', allure.attachment_type.TEXT)
