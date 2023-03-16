import allure
from yaf.data.parsers.cache_command_extractor import parse
from .base_operations import Base


class CacheSteps(Base):

    @staticmethod
    @allure.step('Создать схему в Cache')
    def create_cache_scheme(client_name, schema):
        allure.attach(
            CacheSteps.create_delete_opr(client_name=client_name,
                                         schema=schema,
                                         need_delete=False),
            'Получена схема: ',
            allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Удалить схему в Cache')
    def delete_cache_scheme(client_name, schema):
        allure.attach(
            CacheSteps.create_delete_opr(client_name=client_name,
                                         schema=schema,
                                         need_delete=True),
            'Удалена схема: ',
            allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Записать значение в Cache')
    def put_into_cache(client_name, text):
        client = CacheSteps.connections.get_client(client_name)
        parsed_dict = parse(CacheSteps.render_and_attach(text))
        client.put_to_cache(scheme=parsed_dict['scheme'],
                            key=parsed_dict['key'],
                            value=parsed_dict['value'],
                            expired=parsed_dict['expired'])
        info_mess = 'Документ записанный в Cache - \n'
        CacheSteps.attach_request_block(info_mess=info_mess,
                                        body=parsed_dict['value'],
                                        save=True)

    @staticmethod
    @allure.step('Получить значение из Cache')
    def get_from_cache(client_name, text):
        client = CacheSteps.connections.get_client(client_name)
        parsed_dict = parse(CacheSteps.render_and_attach(text))
        response = client.get_to_cache(scheme=parsed_dict['scheme'],
                                       key=parsed_dict['key'])
        info_mess = 'Документ полученный из Cache - \n'
        CacheSteps.attach_response_block(info_mess=info_mess,
                                         body=response)

    @staticmethod
    @allure.step('Удалить из Cache')
    def delete_from_cache(client_name, text):
        client = CacheSteps.connections.get_client(client_name)
        parsed_dict = parse(CacheSteps.render_and_attach(text))
        client.drop_in_cache(scheme=parsed_dict['scheme'],
                             key=parsed_dict['key'],
                             drop_all=parsed_dict['allIn'])
        info_mess = 'Документ удаленный из Cache по ключу - \n'
        if parsed_dict['allIn']:
            info_mess = 'Очищена схема в Cache - \n'
            allure.attach(parsed_dict['scheme'], info_mess,
                          allure.attachment_type.TEXT)
        else:
            allure.attach(parsed_dict['key'], info_mess,
                          allure.attachment_type.TEXT)

########################################################################################################################

    @staticmethod
    def create_delete_opr(client_name, schema, need_delete):
        client = CacheSteps.connections.get_client(client_name)
        schema = parse(schema)['scheme']
        client.get_or_delete_cache_scheme(scheme=schema,
                                          is_delete=need_delete)
        return schema
