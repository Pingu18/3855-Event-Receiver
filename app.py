import connexion
from connexion import NoContent

import requests
import pykafka
from pykafka import KafkaClient
import datetime
import yaml
import json

import logging
from logging import config
from flask_cors import CORS, cross_origin

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    kafka_server = app_config['kafka-conf']['kafka-server']
    kafka_port = app_config['kafka-conf']['kafka-port']
    kafka_topic = app_config['kafka-conf']['kafka-topic']

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.setLevel(logging.DEBUG)


def request_immediate(requestImmediate):

    logger.info("Start of immediate request")

    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics['{}'.format(kafka_topic)]
    producer = topic.get_sync_producer()
    msg = {"type": "requestImmediate",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": requestImmediate}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    print(msg)

    logger.info('Produced message in topic {}: {}'.format(topic.name, msg))

    """
    url = 'http://localhost:8090/request/immediate'
    json_data = requestImmediate
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json=json_data, headers=headers)
    status_code = r.status_code
    logger.info("End of immediate request")
    return NoContent, status_code
    """


def request_scheduled(requestScheduled):

    logger.info("Start of scheduled request")

    client = pykafka.KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics['{}'.format(kafka_topic)]
    producer = topic.get_sync_producer()
    msg = {"type": "requestScheduled",
           "datetime": datetime.datetime.now().strftime("%Y -%m-%dT%H:%M:%S"),
           "payload": requestScheduled}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Produced message in topic {}: {}'.format(topic, msg))

    """
    url = 'http://localhost:8090/request/scheduled'
    json_data = requestScheduled
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, json=json_data, headers=headers)
    status_code = r.status_code
    logger.info("End of scheduled request")
    return NoContent, status_code
    """


if __name__ == '__main__':
    app = connexion.FlaskApp(__name__, specification_dir='')
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
    app.add_api('openapi.yaml')
    app.run(port=8080)
