import allure
from yaf.data.parsers.redis_command_extractor import parse
from .base_operations import Base


class RedisSteps(Base):

    @staticmethod
    @allure.step('Записать значение в Redis')
    def put_into_redis(client_name, text):
        client = RedisSteps.connections.get_client(client_name)
        parsed_dict = parse(RedisSteps.render_and_attach(text))
        client.put_to_cache(key=parsed_dict['key'],
                            value=parsed_dict['value'],
                            expired=parsed_dict['expired'])
        info_mess = 'Документ записанный в Redis - \n'
        RedisSteps.attach_request_block(info_mess=info_mess,
                                        body=parsed_dict['value'],
                                        save=True)

    @staticmethod
    @allure.step('Получить значение из Redis')
    def get_from_redis(client_name, text):
        client = RedisSteps.connections.get_client(client_name)
        parsed_dict = parse(RedisSteps.render_and_attach(text))
        response = client.get_from_cache(key=parsed_dict['key'])
        info_mess = 'Документ полученный из Redis - \n'
        RedisSteps.attach_response_block(info_mess=info_mess,
                                         body=response)

    @staticmethod
    @allure.step('Получить ключи из Redis')
    def get_keys_in_redis(client_name, text, expected):
        client = RedisSteps.connections.get_client(client_name)
        text = RedisSteps.render_and_attach(text)
        response = client.get_keys(key_pattern=text)
        info_mess = 'Полученные ключи из Redis - \n'
        allure.attach('\n'.join(response), info_mess, allure.attachment_type.TEXT)
        if expected.upper() == 'EMPTY':
            assert response == [], f'Ключи по шаблону [{text}] присутствуют!!'
            return
        assert len(response) > 0, f'Ключи по шаблону [{text}] отсутсвуют!!'
        RedisSteps.put_response_to_stash(response)
