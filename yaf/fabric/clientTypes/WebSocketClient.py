import re
import ssl
import websocket
from threading import Thread
from time import sleep, ctime
from websocket._exceptions import WebSocketConnectionClosedException
from yaf.utils.common_constants import SECRETS_DIR


class WSocketCl:
    def __init__(self, config: dict):
        # websocket.enableTrace(True)
        self.url = config['path']
        self.ssl_context = ssl.SSLContext()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.options = {'sslopt': {'context': self.ssl_context},
                        'skip_utf8_validation': True}

        if isinstance(config['ssl']['verify'], str):
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.ssl_context.load_verify_locations(f"{SECRETS_DIR}/{config['ssl']['verify']}")

        if 'cert' in config['ssl']:
            key = f"{SECRETS_DIR}/{config['ssl']['key']}" if 'key' in config['ssl'] else None
            kwargs = {
                "certfile": f"{SECRETS_DIR}/{config['ssl']['cert']}",
                "keyfile": key
            }
            self.ssl_context.load_cert_chain(**kwargs)

        self.interrupt = False
        self.default_kw = {}
        self.events = []

        if config['launch']:
            self.default_kw = {"header": [f"Authorization: Bearer {config['token']}"] if 'token' in config else None}
            self._launch()

    def _launch(self):
        self.ws = websocket.WebSocketApp(url=self.url + self.default_kw['endpoint'],
                                         header=self.default_kw['header'],
                                         on_message=self._on_message,
                                         on_error=self._on_error,
                                         on_close=self._on_close)
        self.events.clear()
        wst = Thread(target=self.ws.run_forever, kwargs=self.options)
        wst.daemon = True
        wst.start()

    def _on_message(self, ws, message):
        event = re.fullmatch(r'(\d+)(.*)', message)
        self.events.append(event.group(2))

    def _on_error(self, ws, error):
        print(f'receive error:\n{error}')
        self.shutdown()

    def _on_close(self, ws, close_status_code, close_msg):
        print('disconnected from server')
        if not self.interrupt:
            print("Retry : %s" % ctime())
            sleep(2)  # retry per 2 seconds
            self._launch()

    def run_container(self, **kwargs):
        print(f'run websocket from step with args:\n{kwargs}')
        self.default_kw = kwargs
        self._launch()
        sleep(0.2)

    def shutdown(self):
        print("\n   shutdown !!\n")
        self.interrupt = True
        try:
            self.ws.close()
        except AttributeError:
            pass

    def send(self, message: str, timeout: int = 5):
        print('send message >>')
        err_msg = f'Не удалось отправить событие за {timeout} сек.\n'
        while timeout > 0:
            try:
                self.ws.send(data=message)
                return
            except WebSocketConnectionClosedException as wse:
                timeout -= 1
                sleep(1)
        raise Exception(err_msg)

    def receive(self, types: str, timeout: int):
        print('get message <<')
        if types.lower() == 'next':
            cur_size = len(self.events)
            t = timeout*10
            while t > 0:
                sleep(0.1)
                t -= 1
                if cur_size != len(self.events) and len(self.events) > 2:
                    return self.events[-1]
            raise Exception(f'Новое событие не полученно за время {timeout} сек.')
        elif len(self.events) == 0:
            raise Exception('Отсутствуют любые события !!')
        else:
            return self.events[-1]
