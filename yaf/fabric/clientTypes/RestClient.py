import requests
from time import sleep
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests_futures.sessions import FuturesSession
from concurrent.futures import Future
from yaf.utils.common_constants import SECRETS_DIR


class RestCl:
    def __init__(self, config: dict):
        self.retry_strategy = Retry(
            total=1,
            status_forcelist=[500, 502, 503, 504],
            method_whitelist=["POST", "GET", "PUT"]
        )
        self.adapter = HTTPAdapter(
            max_retries=self.retry_strategy if not config.get("disable_retryer", False) else 0)
        self.http = requests.Session()
        self.http.verify = f"{SECRETS_DIR}/{config['ssl']['verify']}" \
            if isinstance(config['ssl']['verify'], str) else config['ssl']['verify']
        if config['ssl'].get('cert') is not None:
            certificate = f"{SECRETS_DIR}/{config['ssl']['cert']}"
            self.http.cert = (certificate, f"{SECRETS_DIR}/{config['ssl'].get('key')}") if config['ssl'].get('key') \
                else certificate
        self.async_http = FuturesSession(session=self.http)
        self.timeout = config.get("default_timeout", 30)
        self.http.mount("https://", self.adapter)
        self.http.mount("http://", self.adapter)
        self.base_url = config['path']

    def exchange(self, method, url, headers, body):
        return self.http.request(method=method,
                                 url=url,
                                 headers=headers,
                                 data=body.encode('utf-8') if body else None,
                                 timeout=self.timeout)

    def async_send(self, method, url, headers, body):
        return self.async_http.request(method=method,
                                       url=url,
                                       headers=headers,
                                       data=body.encode('utf-8') if body else None,
                                       timeout=10)

    def async_get(self, future: Future, timeout=10):
        counter = 0
        while future.running():
            sleep(0.1)
            counter += 1
            if counter > (timeout * 10):
                raise Exception(f'Не удалось получить ответ с тамаутом {timeout} сек !!')

        return future.result()
