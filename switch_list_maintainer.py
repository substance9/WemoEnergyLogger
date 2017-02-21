import threading
import time
from ouimeaux.environment import Environment
import logging


class SwitchListMaintainer(threading.Thread):
    _name_list = None
    _env = None
    _config = None

    def __init__(self, config=None, name_list=None, env = None):
        threading.Thread.__init__(self)
        self._name_list = name_list
        self._config = config

    def _connect(self, config):
        raise NotImplementedError()

    def get(self, data):
        self._on_get_data(data)

    def _on_get_data(self, data):
        try:
            self._queue.put(data, block=False)
        except Exception as e:
            print e

    def _process_data(self, data):
        return data

    def send(self, data):
        raise NotImplementedError()

    def on_switch(self, switch):
            logging.debug("Switch found! " + str(switch.name))

    def find_energy_meter(self):
        self._env.discover(self._config['discover_wait_time'])
        self._name_list = self._env.list_switches()
        logging.debug("List of local switches: " + str(self._env.list_switches()))



    def setList(self, name_list):
        self._name_list = name_list

    def getList(self):
        return self._name_list

    def setEnv(self, env):
        self._env = env

    def run(self):
        while(True):
            self.find_energy_meter()
            time.sleep(self._config['update_interval'])
