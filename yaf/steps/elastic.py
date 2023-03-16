import datetime
import allure
from yaf.data.parsers.elk_command_extractor import parse
from .base_operations import Base


class ElkSteps(Base):

    @staticmethod
    @allure.step('Получить документ из ELK по id')
    def get_doc_from_elk(client_name, text):
        client = ElkSteps.connections.get_client(client_name)
        parsed_dict = parse(ElkSteps.render_and_attach(text))
        response = client.get_doc(index_es=parsed_dict['index'],
                                  type_es=parsed_dict['doc_type'],
                                  id_es=parsed_dict['id'])
        info_mess = f'Документ полученный из ELK - \n'
        ElkSteps.attach_response_block(info_mess=info_mess,
                                       body=response)

    @staticmethod
    @allure.step('Получить документ из Elasticsearch по индексу и содержимому')
    def get_doc_from_elk_by_index_and_query(client_name, text):
        client = ElkSteps.connections.get_client(client_name)
        parsed_dict = parse(ElkSteps.render_and_attach(text))
        index = str(parsed_dict['index'])
        if 'current_date' in index:
            now = datetime.date.today().strftime("%Y.%m.%d")
            index = index.replace('current_date', now)
        response = client.get_doc_by_index_and_query(index_es=index,
                                                     query=parsed_dict['query'])
        info_mess = f'Документ полученный из ELK - \n'
        ElkSteps.attach_response_block(info_mess=info_mess,
                                       body=response)

    @staticmethod
    @allure.step('Поиск документов в ELK по KibanaQuery')
    def search_docks_in_elk(client_name, text):
        client = ElkSteps.connections.get_client(client_name)
        parsed_dict = parse(ElkSteps.render_and_attach(text))
        response = client.search_docs(LAST=parsed_dict['before'],
                                      INDEX=parsed_dict['index'],
                                      FIELD=parsed_dict['field'],
                                      KQL=parsed_dict['kql'])
        info_mess = f'Полученные документы по запросу в ELK - \n'
        ElkSteps.attach_response_block(info_mess=info_mess,
                                       body=response)

    @staticmethod
    @allure.step('Расширенный поиск документов в ELK по KibanaQuery')
    def extended_search_docks_in_elk(client_name, args):
        client = ElkSteps.connections.get_client(client_name)
        # TODO:: copy of args + LAST
        args['KQL'] = ElkSteps.perform_replacement_and_return(args['KQL'])
        scroll_info = ''
        for k, v in args.items():
            scroll_info += f"\n{k}: {v}"
        ElkSteps.render_and_attach(scroll_info)
        response = client.search_docs(**args)
        info_mess = f'Полученные документы по запросу в ELK - \n'
        ElkSteps.attach_response_block(info_mess=info_mess,
                                       body=response)
