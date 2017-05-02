import time
import yaml
import logging
import threading
import queue

_config_file = './config.yml'
_config = {}

from resource import METERS_NAME_SET
from switch_set_maintainer import SwitchSetMaintainer
#from switch_querier import SwitchQuerier
from tippers_sender import TippersSender

def get_config():
    try:
        config_f = open(_config_file)
    except IOError:
        #sys.stdout.write("Error: can\'t find config file or read data from: config.yml\n")
        logging.error("Error: can\'t find config file or read data from: config.yml\n")
        return None
    else:
        config = yaml.load(config_f)
        config_f.close()
        return config


def main():
    ###########################################
    # System Initialization, Read config file
    ###########################################
    logging.basicConfig(level=logging.INFO)
    logging.debug("Program start in main() function")
    global _config
    _config = get_config()
    if _config == None:
        logging.error("Config is Empty")
        return
    logging.debug("Loaded config: " + str(_config))


    ###########################################
    # Set up the important data structures
    ###########################################
    # The set that includes the names of the Wemo switches
    global METERS_NAME_SET
    METERS_NAME_SET = set()

    # The queue that contains the wemo energy data, the elements are
    # put by the queriers and get by the sender
    data_queue = queue.Queue(_config['queue_max_size'])


    ###########################################
    # Start Ouimeaux Env
    ###########################################
#    meters_name_set = set()
#    env = Environment(on_switch)
 #   env.start()


    ###########################################
    # Start Switch Set Maintainer
    ###########################################
    try:
        maintainer = SwitchSetMaintainer(
            config=_config,
            name_set=METERS_NAME_SET,
            data_queue=data_queue
        )
        maintainer.setDaemon(True)
    except Exception as e:
        logging.error(e)
        logging.error("Can\'t create SwitchSetMaintainer")
    else:
        maintainer.start()

    try:
        tippers_sender = TippersSender(
            config=_config["tippers_http_sender"],
            data_queue=data_queue
        )
        tippers_sender.setDaemon(True)
    except Exception as e:
        logging.error(e)
        logging.error("ERROR: Can\'t create Sender")
    else:
        tippers_sender.start()

    #update_meters_name_list()
    time.sleep(_config['switch_set_maintainer']['discover_wait_time'])

    # Main Loop Start
    while(True):
        pass


if __name__ == "__main__":
    main()
