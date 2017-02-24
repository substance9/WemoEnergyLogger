from ouimeaux.environment import Environment
import time
import yaml
import logging
import threading

from switch_list_maintainer import SwitchListMaintainer
from tippers_sender import TippersSender

_config_file = './config.yml'
env = None
_config = {}

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


def on_switch(switch):
    logging.debug("Switch found! " + str(switch.name))

def update_meters_name_list():
    global _config
    threading.Timer(_config["switch_list_maintainer"]["update_interval"], update_meters_name_list).start()
    global env
    env.discover(_config["switch_list_maintainer"]["discover_wait_time"])

def main():
    # System Initialization, Read config file
    logging.basicConfig(level=logging.INFO)
    logging.debug("Program start in main() function")
    global _config
    _config = get_config()
    if _config == None:
        logging.error("Config is Empty")
        return
    logging.debug("Loaded config: " + str(_config))

    meters_name_list = []
    global env
    env = Environment(on_switch)
    env.start()
    env.discover(20)
    # Find energy meters in local network and maintain the list of meters periodically
    #try:
    #    maintainer = SwitchListMaintainer(
    #        config=_config['switch_list_maintainer'])
    #    maintainer.setDaemon(True)
    #except Exception as e:
    #    logging.error(e)
    #    logging.error("ERROR: Can\'t create SwitchListMaintainer")
    #else:
    #    maintainer.setEnv(env)
    #    maintainer.setList(meters_name_list)
    #    maintainer.start()

    try:
        tippers_sender = TippersSender(
            config=_config["tippers_http_sender"]
        )
        tippers_sender.setDaemon(True)
    except Exception as e:
        logging.error(e)
        logging.error("ERROR: Can\'t create Sender")
    else:
        tippers_sender.start()

    #update_meters_name_list()
    time.sleep(_config['switch_list_maintainer']['discover_wait_time'])

    # Main Loop Start
    while(True):
        # Get up-to-date meter list
        meters_name_list = env.list_switches()
        for meter_name in meters_name_list:
            meter_instance = None
            meter_data = {}
            try:
                meter_instance = env.get_switch(meter_name)
            except Exception as e:
                logging.error("Error when trying to get meter instance")
                logging.error(e)
            if meter_instance is not None:
                try:
                    meter_data["id"] = meter_name
                    meter_data["current_power"] = meter_instance.current_power
                    meter_data["today_seconds"] = meter_instance.today_on_time
                    meter_data["state"] = meter_instance.get_state()
                except Exception as e:
                    logging.error("Error when trying to get meter data")
                    logging.error(e)

            if meter_data:
                tippers_sender.push(meter_data)



        time.sleep(_config['data_collector']['sensing_interval'])


if __name__ == "__main__":
    main()
