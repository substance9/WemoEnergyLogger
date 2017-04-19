import json
import datetime
import requests
import threading
import queue
import logging


class TippersSender(threading.Thread):
    _queue = None
    _config = None

    def __init__(self, queue_size=4096, config=None, data_queue=queue.Queue()):
        threading.Thread.__init__(self)
        self._queue = data_queue
        self._config = config

    def _connect(self, config):
        # self._port = int(self._config['port'])
        self._url = self._config['url']

        self._headers = {"Accept": "application/json",
                         "Content-type": "application/json"}

    def _process_data(self, data):
        observation = {}
        #observation['observation_type'] = self._config["observation_type"]
        observation['type'] = "2"
        observation['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        #observation['accuracy'] = 0
        observation['sensor_id'] = data['id']

        payload = {}
        payload["currentMilliWatts"] = data["current_power"]
        payload["onTodaySeconds"] = data["today_seconds"]
        payload["currentState"] = data["state"]
        observation['payload'] = payload
        return [observation]

    def send(self, data_processed):
        message_data = json.dumps(data_processed)
        logging.info("Sending to TIPPERS REST API. The Message is:")
        logging.info(message_data)
        try:
            requests.request(method='POST',
                             url=self._url,
                             headers=self._headers,
                             data=message_data)
            pass
        except Exception as e:
            logging.error(e)
            logging.error("ERROR: Failed to PUT data to TIPPERS")

    def run(self):
        self._connect(self._config)
        while(True):
            data = self._queue.get(block=True)
            #TODO: I am not sure if the blocking queue will cause any issue. Need to be studied carefully. If use non-blocking queue, need to handle the empty exception
            processed_data = self._process_data(data)
            self.send(processed_data)
