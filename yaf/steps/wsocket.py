import allure
from yaf.data.parsers.ws_command_extractor import parse
from .base_operations import Base


class WSocketSteps(Base):

    @staticmethod
    @allure.step('Создать WebSocket соединение')
    def ws_create_connection(client_name, instructions):
        client = WSocketSteps.connections.get_client(client_name)
        instructions = WSocketSteps.perform_replacement_and_return(instructions)
        options = parse(instructions)
        client.run_container(**options)
        info_mess = 'Запущено содинение по WebSocket - \n'
        allure.attach(f'CLIENT: {client_name}\n{instructions}',
                      info_mess,
                      allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Получить событие по WebSocket\'у')
    def receive_from_ws(client_name, instructions):
        client = WSocketSteps.connections.get_client(client_name)
        options = parse(WSocketSteps.perform_replacement_and_return(instructions))
        response = client.receive(timeout=options['timeout'],
                                  types=options['get'])
        info_mess = 'Документ полученный из WebSocket - \n'
        WSocketSteps.attach_response_block(info_mess=info_mess,
                                           body=response)

    @staticmethod
    @allure.step('Отправить событие по WebSocket\'у')
    def send_event_to_ws(client_name, message):
        client = WSocketSteps.connections.get_client(client_name)
        message = WSocketSteps.perform_replacement_and_return(message)
        client.send(message=message)
        info_mess = 'Документ отправленный по WebSocket - \n'
        WSocketSteps.attach_request_block(info_mess=info_mess,
                                          body=message,
                                          save=True)
