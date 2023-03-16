import json
import allure
from yaml import safe_load
from tabulate import tabulate
from .base_operations import Base
from google.protobuf.text_format import MessageToString


class GrpcSteps(Base):

    @staticmethod
    @allure.step('Отправить GRPC запрос')
    def send_grpc_request(client_name, payload):
        payload = GrpcSteps.render_and_attach(payload)
        elements: dict = safe_load(payload)
        serv_name = elements.pop('SERVICE')
        rpc_name = elements.pop('RPC')
        msg_type = next(iter(elements))
        GrpcSteps.put_request_to_stash(elements)
        client = GrpcSteps.connections.get_client(client_name)
        response = client.performer(service=serv_name,
                                    rpc=rpc_name,
                                    message=msg_type,
                                    args=elements[msg_type])
        if isinstance(response, Exception):
            err_mess = 'Ошибка полученная по PROTOBUF протоколу - \n'
            allure.attach(str(response), err_mess, allure.attachment_type.TEXT)
        elif response is not None:
            info_mess = 'Объект полученный по PROTOBUF протоколу - \n'
            resp_str = MessageToString(response, as_utf8=True)
            allure.attach(resp_str, info_mess, allure.attachment_type.TEXT)
        else:
            info_mess = 'Отсутствует ответ по PROTOBUF протоколу либо равен None - \n'
            allure.attach('None', info_mess, allure.attachment_type.TEXT)
        GrpcSteps.put_response_to_stash(response)

    @staticmethod
    @allure.step('Отправить GRPC запрос в виде json')
    def send_json_like_grpc_request(client_name, payload):
        payload = GrpcSteps.perform_replacement_and_return(payload)
        elements: dict = safe_load(payload)
        serv_name = elements.pop('SERVICE')
        rpc_name = elements.pop('RPC')
        msg_type = next(iter(elements))
        allure.attach(tabulate(tabular_data=[('SERVICE', serv_name),
                                             ('RPC', rpc_name),
                                             ('TYPE', msg_type)],
                               tablefmt='fancy_grid'),
                      'Детали запроса -', allure.attachment_type.TEXT)
        GrpcSteps.attach_request_block(info_mess='Тело запроса -', save=True,
                                       body=elements[msg_type])
        client = GrpcSteps.connections.get_client(client_name)
        response = client.json_performer(service=serv_name,
                                         rpc=rpc_name,
                                         message=msg_type,
                                         json_representation=elements[msg_type])
        if isinstance(response, Exception):
            GrpcSteps.transform_grpc_error(response)
        elif response is None:
            info_mess = 'Отсутствует ответ по PROTOBUF протоколу либо равен None - \n'
            allure.attach('None', info_mess, allure.attachment_type.TEXT)
        else:
            GrpcSteps.attach_response_block(info_mess='Объект полученный по PROTOBUF протоколу - \n',
                                            body=response)

########################################################################################################################

    @staticmethod
    def transform_grpc_error(error: Exception):
        err_mess = f'Получена ошибка {str(type(error))} - \n'
        err_json_str = json.dumps({
            'status': str(error.args[0].code),
            'details': error.args[0].details,
            'debug_error_string': error.args[0].debug_error_string,
            'cancelled': error.args[0].cancelled
        }, indent=2, ensure_ascii=False)
        allure.attach(err_json_str, err_mess, allure.attachment_type.JSON)
        GrpcSteps.put_response_to_stash(err_json_str)
