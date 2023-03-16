from json import loads
from bson.json_util import dumps
from pymongo import MongoClient
from pymongo.results import InsertManyResult
from yaf.utils.common_constants import EMPTY


class MongoCl:
    def __init__(self, config: dict):
        config.pop('name')
        self.client = MongoClient(**config)

    def insert_data(self, database, collection_name, data: str):
        collection = eval(f'self.client.{database}.{collection_name}')
        data_obj = loads(data)
        result = collection.insert_many(data_obj) \
            if isinstance(data_obj, list) \
            else collection.insert_one(data_obj)
        assert result.acknowledged, f'Не удалось произвести вставку данных !!'
        return '\n'.join([str(x) for x in result.inserted_ids]) if isinstance(result, InsertManyResult) \
            else str(result.inserted_id)

    def find_data(self, database, collection_name, fields: str, marker: str, sort_rule: list):
        show_fields = {field.replace('!', EMPTY): int('!' not in field)
                       for field in (fields.split(',') if fields else [])}
        collection = eval(f'self.client.{database}.{collection_name}')
        mark_obj = loads('{}' if marker is None else marker)
        result = list(collection.find(mark_obj, show_fields).sort(*sort_rule))
        return dumps(result, ensure_ascii=False)

    def update_data(self, database, collection_name, marker: str, data: str):
        collection = eval(f'self.client.{database}.{collection_name}')
        result = collection.update_many(loads(marker), loads(data))
        assert result.acknowledged, f'Не удалось произвести обновление данных !!'
        return result.raw_result['updatedExisting'], result.raw_result['nModified']

    def delete_data(self, database, collection_name, marker: str):
        collection = eval(f'self.client.{database}.{collection_name}')
        result = collection.delete_many(loads(marker))
        assert result.acknowledged, f'Не удалось произвести удаление данных !!'
        return result.deleted_count
