import threading
import time
from ouimeaux.environment import Environment
import logging
import queue

from switch_querier import SwitchQuerier
from energy_logger import METERS_NAME_SET

class SwitchSetMaintainer(threading.Thread):

    def __init__(self, config=None, name_set=set(), data_queue=queue.Queue()):
        threading.Thread.__init__(self)
        self._name_set = METERS_NAME_SET
        self._config = config['switch_set_maintainer']
        self._config_querier = config['switch_querier']
        self._data_queue = data_queue
        self._env = Environment()

    def find_energy_meter(self):
        self._env.discover(self._config['discover_wait_time'])
        logging.debug("List of local switches: " + str(self._env.list_switches()))
        name_set_current = set(self._env.list_switches())
        switch_names_new = name_set_current - self._name_set

        for switch_name in switch_names_new:
            logging.info("Found new switch" + str(switch_name) + ". Getting the instance of the switch")
            switch_instance = None
            try:
                switch_instance = self._env.get_switch(switch_name)
            except Exception as e:
                logging.error("Error when trying to get meter instance")
                logging.error(e)
            if switch_instance is not None:
                logging.info("Creating the Querier thread for the switch " + str(switch_name))
                try:
                    querier = SwitchQuerier(
                        config=self._config_querier,
                        switch_name=switch_name,
                        switch_instance=switch_instance,
                        data_queue=self._data_queue,
                        name_set=self._name_set
                    )
                    querier.setDaemon(True)
                except Exception as e:
                    logging.error("Error when trying to create Querier thread")
                    logging.error(e)
                else:
                    querier.start()
                    self._name_set.add(switch_name)


    def run(self):
        self._env.start()
        while(True):
            self.find_energy_meter()
            time.sleep(self._config['update_interval'])
