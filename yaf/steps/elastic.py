import datetime
import allure
from yaf.data.parsers.elk_command_extractor import parse
from .base_operations import Base


class ElkSteps(Base):

    @staticmethod
    @allure.step('Get document from Elasticsearch by id')
    def get_doc_from_elk(client_name, text):
        client = ElkSteps.connections.get_client(client_name)
        parsed_dict = parse(ElkSteps.render_and_attach(text))
        response = client.get_doc(index_es=parsed_dict['index'],
                                  type_es=parsed_dict['doc_type'],
                                  id_es=parsed_dict['id'])
        info_mess = f'Document received from ELK - \n'
        ElkSteps.attach_response_block(info_mess=info_mess,
                                       body=response)

    @staticmethod
    @allure.step('Get document from Elasticsearch by index and content')
    def get_doc_from_elk_by_index_and_query(client_name, text):
        client = ElkSteps.connections.get_client(client_name)
        parsed_dict = parse(ElkSteps.render_and_attach(text))
        index = str(parsed_dict['index'])
        if 'current_date' in index:
            now = datetime.date.today().strftime("%Y.%m.%d")
            index = index.replace('current_date', now)
        response = client.get_doc_by_index_and_query(index_es=index,
                                                     query=parsed_dict['query'])
        info_mess = f'Document received from ELK - \n'
        ElkSteps.attach_response_block(info_mess=info_mess,
                                       body=response)

    @staticmethod
    @allure.step('Search for documents in ELK using KibanaQuery')
    def search_docks_in_elk(client_name, text):
        client = ElkSteps.connections.get_client(client_name)
        parsed_dict = parse(ElkSteps.render_and_attach(text))
        response = client.search_docs(LAST=parsed_dict['before'],
                                      INDEX=parsed_dict['index'],
                                      FIELD=parsed_dict['field'],
                                      KQL=parsed_dict['kql'])
        info_mess = f'Received documents upon request in ELK - \n'
        ElkSteps.attach_response_block(info_mess=info_mess,
                                       body=response)

    @staticmethod
    @allure.step('Advanced search for documents in ELK using KibanaQuery')
    def extended_search_docks_in_elk(client_name, args):
        client = ElkSteps.connections.get_client(client_name)
        # TODO:: copy of args + LAST
        args['KQL'] = ElkSteps.perform_replacement_and_return(args['KQL'])
        scroll_info = ''
        for k, v in args.items():
            scroll_info += f"\n{k}: {v}"
        ElkSteps.render_and_attach(scroll_info)
        response = client.search_docs(**args)
        info_mess = f'Received documents upon request in ELK - \n'
        ElkSteps.attach_response_block(info_mess=info_mess,
                                       body=response)
