import io
import sys
import json
import socket
import threading
from time import sleep
from typing import List, Dict
from avro.schema import parse as avsc_parse
from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from yaf.utils.common_constants import RESOURCES_DIR, SECRETS_DIR
from yaf.utils.json_static_param import is_payload_json
from random import randrange


def create_producer(config):
    conf = {'client.id': socket.gethostname()}
            # 'queue.buffering.max.ms': 5,
            # 'socket.blocking.max.ms': 1,
    conf.update(get_network_settings(config))
    return Producer(conf)


class KafkaRecord:
    def __init__(self, topic, partition, key, headers, value):
        self.topic = topic
        self.partition = partition
        self.key = key
        self.headers = headers
        self.value = value


class KafkaListener(threading.Thread):
    def __init__(self, config: dict):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.network = get_network_settings(config)
        self.out_topics = config['out_topics']
        # self.group_id = config['group_id']
        # TODO:: remove crutch for multi-process test runs
        self.group_id = config['group_id'] + f'{randrange(1000)}'
        self.auto_offset_reset = config.get('auto_offset_reset', 'latest')
        self._consumed_list: List[KafkaRecord] = []

    def stop(self):
        self.stop_event.set()

    def get_kafka_queue(self):
        return self._consumed_list

    def run(self):
        conf = {
            "api.version.request": True,
            "enable.auto.commit": False,
            "group.id": self.group_id,
            "default.topic.config": {
                "auto.offset.reset": self.auto_offset_reset
            }
        }
        conf.update(self.network)
        consumer = Consumer(conf)

        if isinstance(self.out_topics, str):
            consumer.subscribe([self.out_topics])
        else:
            consumer.subscribe(self.out_topics)

        while not self.stop_event.is_set():
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # TODO:: read protobuf messages
                self._consumed_list.append(
                    KafkaRecord(msg.topic(),
                                msg.partition(),
                                msg.key(),
                                msg.headers(),
                                msg.value()))
                # TODO:: DO NOT USE with conf => { "enable.auto.commit": True } !!
                # consumer.commit(asynchronous=False)
        consumer.close()


def avro_serializer(message, avro_schema_name):
    writer = DatumWriter(avsc_parse(open(f'{RESOURCES_DIR}/{avro_schema_name}').read()))
    bytes_writer = io.BytesIO()
    encoder = BinaryEncoder(bytes_writer)
    writer.write(json.loads(message), encoder)
    return bytes_writer.getvalue()


def avro_deserializer(byte_msg, reader):
    decoder = BinaryDecoder(io.BytesIO(byte_msg))
    return json.dumps(reader.read(decoder), ensure_ascii=False)


def delivery_report(err, msg):
    if err is not None:
        print('n\nError delivered msg ---> {}'.format(err))
    else:
        print("\n\nInfo delivered msg --->  \nTOPIC: {}\nPARTITION: {}\nKEY: {}\nHEADERS: {}\nVALUE: {}\n"
              .format(msg.topic(), msg.partition(), msg.key(), msg.headers(), msg.value()))


def get_network_settings(config: dict):
    network_settings = {'bootstrap.servers': config['bootstrap_servers']}
    if config['ssl'].get('cert') is not None:
        network_settings["ssl.certificate.location"] = f"{SECRETS_DIR}/{config['ssl']['cert']}"
        network_settings["security.protocol"] = "ssl"
    if config['ssl'].get('key') is not None:
        network_settings["ssl.key.location"] = f"{SECRETS_DIR}/{config['ssl']['key']}"
    if config['ssl'].get('verify', False):
        network_settings["ssl.ca.location"] = f"{SECRETS_DIR}/{config['ssl']['verify']}"
    return network_settings


class KafkaCl:
    def __init__(self, config: dict):
        # TODO:: make it optional
        self._in_topic = config['in_topics']
        self._pop_when_find = config.get('pop_when_find', False)
        self._producer = create_producer(config)
        # TODO:: launch listener when it required
        self._listener = KafkaListener(config)
        self._listener.start()

    def shutdown(self):
        sleep(0.5)
        self._listener.stop()

    def send_message(self,
                     message,
                     topic=None,
                     partition=-1,
                     key=None,
                     headers=None):

        if is_payload_json(message):
            message = json.dumps(json.loads(message), ensure_ascii=False).encode('utf8').decode()

        headers_dict: Dict[str, List[str]] = {}
        if headers is not None:
            for val in headers.keys():
                headers_dict[val] = headers[val].encode()
        try:
            if topic is None:
                topic = self._in_topic
            self._producer.produce(
                topic=topic,
                value=message,
                partition=partition,
                key=key,
                headers=headers_dict,
                on_delivery=delivery_report)
            assert self._producer.flush(timeout=15) == 0
        except Exception as e:
            raise Exception(f"Could not send to topic {topic}\n{e}")

    def get_last_message_from(self, topic: str, partition: int = 0):
        try:
            return [
                x for x in self._listener.get_kafka_queue()
                if x.topic == topic
                and (True if partition == -1 else x.partition == partition)
            ][-1]
        except IndexError:
            raise Exception(f'Missing records for topic: {topic} '
                            f'and partitions: {"all" if partition == -1 else partition}')

    def find_message_by_mark(self, marker: str, time, avsc=None):
        count = 0
        result = None
        already_checked = 0
        avro_reader = DatumReader(avsc_parse(open(f'{RESOURCES_DIR}/{avsc}').read())) if avsc else None
        while count < time * 10:
            queue = self._listener.get_kafka_queue()[already_checked:]
            if len(queue) == 0:
                count += 1
                sleep(0.1)
                continue
            pos = 0
            for x in queue:
                pos += 1
                value = x.value
                if isinstance(value, bytes) and avsc:
                    try:
                        value = avro_deserializer(value, avro_reader)
                    except: pass
                elif isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8")
                    except: pass
                if isinstance(value, str) and value.__contains__(marker):
                    x.value = value
                    result = x
                    print(f"size:{len(queue)} pos:{pos}")
                    if self._pop_when_find:
                        self._listener.get_kafka_queue().remove(x)
                    break

            print(f"main size:{len(queue) + already_checked} \talready checked:{already_checked} \ton search:{len(queue)}")
            already_checked = already_checked + len(queue)
            if result is not None:
                break
            sleep(0.1)
            count += 1
        if result is not None:
            print("\n\nMatched consumed msg --->  \nTOPIC: {}\nPARTITION: {}\nKEY: {}\nHEADERS: {}\nVALUE: {}\n"
                  .format(result.topic, result.partition, result.key, result.headers, result.value))
            return result
        else:
            raise AssertionError(f"Could not find message from Kafka by marker [ {marker} ] by timeout [ {time}-sec ]")

# TODO:: new method with search msg by condition and proto decode
