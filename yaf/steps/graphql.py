import allure
from json import loads, dumps
from .base_operations import Base


class GraphQLSteps(Base):

    @staticmethod
    @allure.step('Send GraphQl request')
    def send_graphql_request(client_name, payload):
        payload = GraphQLSteps.perform_replacement_and_return(payload)
        elements = loads(payload)
        client = GraphQLSteps.connections.get_client(client_name)
        info = f"OPERATION: {elements['operationName']}\n\n" \
               f"VARIABLES: {dumps(elements['variables'], indent=2, ensure_ascii=False)}\n\n" \
               f"QUERY:     {elements['query']}"
        GraphQLSteps.attach_request_block(info_mess='GraphQl request - \n',
                                          body=info,
                                          save=False)
        response = client.exchange(operation_name=elements['operationName'],
                                   variables=elements['variables'],
                                   query=elements['query'])
        info_mess = 'Document received from GraphQl - \n'
        GraphQLSteps.attach_response_block(info_mess=info_mess,
                                           body=response)
