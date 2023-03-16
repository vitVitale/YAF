import ssl
from pyignite import Client
# from pyignite.datatypes import DataObject
from yaf.utils.common_constants import SECRETS_DIR


class CacheCl:
    def __init__(self, config: dict):
        ignite_prop = {k: v for (k, v) in config.items() if k in ['username', 'password']}
        addresses = [(x.split(':')[0], int(x.split(':')[1])) for x in config['addresses']]
        if config.get('ssl') and config['ssl']['enable']:
            def complete_paths(key: str):
                cert_name = config['ssl'].get(key)
                if cert_name:
                    return f'{SECRETS_DIR}/{cert_name}'
                return cert_name

            certs_req = eval(f"ssl.{config['ssl'].get('cert_reqs')}") \
                if config['ssl'].get('cert_reqs') else ssl.CERT_NONE
            ignite_prop.update({
                "use_ssl": True,
                "ssl_cert_reqs": certs_req,
                "ssl_keyfile": complete_paths('keyfile'),
                "ssl_keyfile_password": config['ssl'].get('keyfile_password'),
                "ssl_certfile": complete_paths('certfile'),
                "ssl_ca_certfile": complete_paths('ca_certfile')
            })
        self.client = Client(**ignite_prop)
        self.client.connect(addresses)

    def get_or_delete_cache_scheme(self, scheme, is_delete: bool):
        if is_delete:
            n = self.client.get_cache(scheme).destroy
        else:
            self.client.get_or_create_cache(scheme)

    def put_to_cache(self, scheme, key, value, expired):
        cache_sc = self.client.get_cache(scheme)
        if expired:
            expired = int(expired)*1000
            cache_sc.with_expire_policy(create=expired, update=expired).put(key=key, value=value)
        else:
            cache_sc.put(key=key, value=value)

    def get_to_cache(self, scheme, key):
        response = self.client.get_cache(scheme).get(key=key)
        if response is not None:
            return response
        raise Exception(f'Не удалось получить обект из [{scheme}] по ключу [{key}] !!')

    def drop_in_cache(self, scheme, key, drop_all: bool):
        if drop_all:
            self.client.get_cache(scheme).remove_all()
        else:
            self.client.get_cache(scheme).remove_key(key=key)
