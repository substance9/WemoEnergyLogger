import time
import threading
import queue
import logging

class SwitchQuerier(threading.Thread):

    def __init__(self, config=None, switch_name=None, switch_instance=None, data_queue=queue.Queue(), name_set=set()):
        threading.Thread.__init__(self)
        self._config = config
        self._data_queue = data_queue
        self._switch_instance = switch_instance
        self._name_set = name_set
        self._switch_name = switch_name

    def get_data(self):
        data = {}
        data["id"] = self._switch_name
        data["current_power"] = self._switch_instance.current_power
        data["today_seconds"] = self._switch_instance.today_on_time
        data["state"] = self._switch_instance.get_state()
        return data

    def send_data(self, data):
        self._data_queue.put(data)

    def run(self):
        while (True):
            data = self.get_data()
            self.send_data(data)
            time.sleep(self._config["sensing_interval"])


