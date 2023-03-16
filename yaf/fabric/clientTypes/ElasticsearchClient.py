import re
import json
import time
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from yaf.utils.common_constants import SECRETS_DIR
from yaf.utils.injection_ops import evaluate_injection


class ElasticCl:
    def __init__(self, config: dict):
        es_props = {"hosts": config['hosts'], "http_auth": None}
        if all(item in config.keys() for item in ['username', 'password']):
            es_props['http_auth'] = (config['username'], config['password'])
        if 'ssl' in config:
            for k, v in config['ssl'].items():
                es_props[k] = f"{SECRETS_DIR}/{v}"
        self.client = Elasticsearch(**es_props)
        ''' health check '''
        self.client.info()

    def get_doc(self, index_es, type_es, id_es):
        try:
            body = self.client.get(index=index_es,
                                   doc_type=type_es,
                                   id=id_es)['_source']
            return json.dumps(body,
                              indent=2,
                              ensure_ascii=False)
        except Exception as ex:
            raise Exception(f'Не удалось получить документ!\n'
                            f'{ex.__cause__}')

    def get_doc_by_index_and_query(self, index_es, query):
        body = None
        try:
            for i in range(3):
                body = self.client.search(index=index_es,
                                          body=json.loads(query))
                if len(body.get('hits').get('hits')) != 0:
                    break
                else:
                    time.sleep(5)

            # поля эластика возвращаются, как строки, поэтому нужно их "зачистить" от лишних кавычек и обратных слешей
            temp = re.sub(r'(?<=[^ ])\\"(?=[^"])', '"', json.dumps(body,
                                                                   indent=2,
                                                                   ensure_ascii=False))

            return re.sub(r'"(?=[{])|(?<=[}])"', '', temp)

        except Exception as ex:
            raise Exception(f'Не удалось получить документ!\n'
                            f'{ex.__cause__}')

    def search_docs(self, INDEX, KQL, FIELD=None, SORT=None, LAST=None, TRANSFORM=None):
        query = {
            'query': {'bool': {'must': [{
                'query_string': {
                    'query': KQL
                }}]}}}
        if LAST is not None:
            query['query']['bool']['must'].append({'range': {'@timestamp': {'gte': f'now-{LAST}', 'lte': 'now'}}})
        if FIELD is not None:
            query['query']['bool']['must'][0]['query_string']['default_field'] = FIELD
        if SORT is not None:
            query['sort'] = SORT
        answers = []
        try:
            for hit in scan(self.client,
                            preserve_order=True,
                            query=query,
                            index=INDEX,
                            scroll="1m",
                            request_timeout=10):
                answers.append(hit['_source'])
        except Exception as ex:
            raise Exception(f'Не удалось выполнить запрос!\n'
                            f'{ex.__cause__}')
        if TRANSFORM:
            answers = evaluate_injection(expression=TRANSFORM, answers=answers)
        return json.dumps(answers,
                          indent=2,
                          ensure_ascii=False)
