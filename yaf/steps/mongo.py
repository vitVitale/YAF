import allure
from .base_operations import Base
from yaf.data.parsers.mongo_command_extractor import parse


class MongoSteps(Base):

    @staticmethod
    @allure.step('Записать объект(ы) в MongoDB')
    def insert_data_into_mongo(client_name, text):
        client = MongoSteps.connections.get_client(client_name)
        parsed_dict = parse(MongoSteps.render_and_attach(text))
        response = client.insert_data(collection_name=parsed_dict['collection'],
                                      database=parsed_dict['database'],
                                      data=parsed_dict['value'])
        allure.attach(response, 'Ключи вставок - \n', allure.attachment_type.TEXT)
        MongoSteps.attach_request_block(info_mess='Объекты записанные в Mongo - \n',
                                        body=parsed_dict['value'],
                                        save=True)

    @staticmethod
    @allure.step('Получить объект(ы) из MongoDB')
    def find_data_in_mongo(client_name, text, expected):
        client = MongoSteps.connections.get_client(client_name)
        parsed_dict = parse(MongoSteps.render_and_attach(text))
        response = client.find_data(collection_name=parsed_dict['collection'],
                                    database=parsed_dict['database'],
                                    sort_rule=parsed_dict['sort'],
                                    fields=parsed_dict['fields'],
                                    marker=parsed_dict['filter'])
        info_mess = 'Объекты полученные в Mongo - \n'
        if expected.upper() != 'EMPTY':
            assert response != '[]', 'Получена пустая выдача !!'
            MongoSteps.attach_response_block(info_mess=info_mess, body=response)
            return
        assert response == '[]', 'Получена не пустая выдача !!'
        allure.attach(response, info_mess, allure.attachment_type.TEXT)

    @staticmethod
    @allure.step('Обновить объект(ы) в MongoDB')
    def update_data_into_mongo(client_name, text, expected):
        client = MongoSteps.connections.get_client(client_name)
        parsed_dict = parse(MongoSteps.render_and_attach(text))
        is_success, count = client.update_data(collection_name=parsed_dict['collection'],
                                               database=parsed_dict['database'],
                                               marker=parsed_dict['filter'],
                                               data=parsed_dict['value'])
        info_mess = 'Запрос выполнен - \n'
        allure.attach(f'Объектов обновлено: {count}',
                      info_mess, allure.attachment_type.TEXT)
        if count == 0:
            flag = 'NO CHANGES ALLOWED' == expected.upper()
            assert flag, 'Ожидаемые изменения не произведены !'

    @staticmethod
    @allure.step('Удалить объект(ы) в MongoDB')
    def remove_data_from_mongo(client_name, text, expected):
        client = MongoSteps.connections.get_client(client_name)
        parsed_dict = parse(MongoSteps.render_and_attach(text))
        count = client.delete_data(collection_name=parsed_dict['collection'],
                                   database=parsed_dict['database'],
                                   marker=parsed_dict['filter'])
        info_mess = 'Запрос выполнен - \n'
        allure.attach(f'Объектов удалено: {count}',
                      info_mess, allure.attachment_type.TEXT)
        if count == 0:
            flag = 'NO CHANGES ALLOWED' == expected.upper()
            assert flag, 'Удаление не произведено !'
