import allure
from .base_operations import Base
from yaf.data.parsers.thrift_command_extractor import parse


class ThriftSteps(Base):

    @staticmethod
    @allure.step('Отправить THRIFT запрос')
    def send_thrift_request(client_name, payload):
        payload = ThriftSteps.render_and_attach(payload)
        elements = parse(payload)
        if elements['args'] is not None:
            ThriftSteps.put_request_to_stash(elements['args'])
        client = ThriftSteps.connections.get_client(client_name)
        response = client.performer(service=elements['service'],
                                    method=elements['method'],
                                    args=elements['args'])
        if response is not None:
            info_mess = 'Объект полученный по Thrift протоколу - \n'
            ThriftSteps.attach_response_block(body=str(response), info_mess=info_mess)
        else:
            ThriftSteps.put_response_to_stash(response)
