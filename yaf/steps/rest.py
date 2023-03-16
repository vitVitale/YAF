import json
import allure
from .base_operations import Base
from yaf.utils.json_static_param import is_payload_json
from yaf.data.parsers.curle_parts_extractor import parse_curl
from yaf.utils.common_constants import HTTP_CODE, EMPTY


class RestSteps(Base):

    @staticmethod
    @allure.step('Отправить REST запрос')
    def send_rest_request(client_name, payload, expected_status):
        payload = RestSteps.render_and_attach(payload)
        elements = parse_curl(payload)
        client = RestSteps.connections.get_client(client_name)
        info_mess = 'Документ отправленный по REST - \n'
        RestSteps.attach_request_block(info_mess=info_mess,
                                       body=elements['body'],
                                       save=True)
        response = client.exchange(elements['method'],
                                   elements['url'],
                                   elements['headers'],
                                   elements['body'])
        RestSteps.attach_response_block(response, None)
        RestSteps.expected_check(expected_status, response.status_code)

    @staticmethod
    @allure.step('Отправить REST запрос асинхронно')
    def send_async_rest_request(client_name, payload):
        payload = RestSteps.render_and_attach(payload)
        elements = parse_curl(payload)
        client = RestSteps.connections.get_client(client_name)
        info_mess = 'Документ отправленный по REST - \n'
        RestSteps.attach_request_block(info_mess=info_mess,
                                       body=elements['body'],
                                       save=True)
        cnt: int = RestSteps.rqCounter
        RestSteps.stash[f'ASYNC_RQ_{cnt if elements["body"] else cnt+1}'] = \
            client.async_send(elements['method'],
                              elements['url'],
                              elements['headers'],
                              elements['body'])

    @staticmethod
    @allure.step('Получить ответ на асинхронный REST запрос')
    def get_async_rest_response(client_name, request_tag, expected_status):
        client = RestSteps.connections.get_client(client_name)
        response = client.async_get(RestSteps.stash[f'ASYNC_{request_tag}'])
        RestSteps.attach_response_block(response, None)
        RestSteps.expected_check(expected_status, response.status_code)

########################################################################################################################

    @staticmethod
    def attach_response_block(response, mess):
        if response.headers is not None:
            info_mess = 'Заголовки полученные из REST запроса - \n'
            msg = '<table border="0">'
            for key in response.headers:
                msg = msg + f'<tr><td>{key}&nbsp;&nbsp;</td><td>{response.headers[key]}</td></tr>'
            msg = msg + '</table>'
            allure.attach(msg, info_mess, allure.attachment_type.HTML)
            RestSteps.stash[f'HEADERS_RS_{Base.rsCounter + 1}'] = response.headers
        if response.text is not None:
            info_mess = 'Документ полученный из REST запроса - \n'
            attach = allure.attachment_type.TEXT
            text = response.text
            if is_payload_json(response.text):
                attach = allure.attachment_type.JSON
                text = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
            # TODO:: add later xml type
            # is_xml = is_payload_xml(body)
            allure.attach(text, info_mess, attach)
            RestSteps.put_response_to_stash(text)
        else:
            info_mess = 'Нет ответного тела!'
            allure.attach('NO BODY!', info_mess, allure.attachment_type.TEXT)

    @staticmethod
    def expected_check(expected_value, actual):
        expected_value = expected_value.replace(HTTP_CODE, EMPTY)
        assert str(actual) == expected_value, f'Http статус [{actual}] не совпал ' \
                                              f'с ожидаемым [{expected_value}] !!'
