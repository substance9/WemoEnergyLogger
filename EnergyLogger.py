from ouimeaux.environment import Environment
import time
import pymysql.cursors
import yaml
import logging

_config_file = './config.yml'


_config = {}
_db_connection = None

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
    if __debug__:
        logging.info("Switch found! " + str(switch.name))

def find_energy_meter():
    global _config
    env = Environment(on_switch)
    env.start()
    env.discover(2)
    logging.debug("List of local switches: " + str(env.list_switches()))

    try:
        logging.debug("Trying to get switch: " + str(_config['wemo']['name']))
        energy_monitor = env.get_switch(_config['wemo']['name'])
    except Exception as e:
        logging.error("Error when trying to get energy meter")
        logging.error(e)
        return None
    else:
        return energy_monitor

def get_db_connection():
    global _config
    db_config = _config['mysql']
    connection = pymysql.connect(host=db_config['host'],
                             user=db_config['user'],
                             password=db_config['password'],
                             db=db_config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    return connection
    

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

    # Find energy meter in local network
    logging.debug("Start to find energy meter in local network")
    energy_meter_instance = None
    while(energy_meter_instance is None):
        energy_meter_instance = find_energy_meter()

    # Initilize DB Connection
    logging.debug("Start to Connect to DB")
    global _db_connection
    _db_connection = get_db_connection()

    # Main Loop Start
    while(True):
        # Read Smart Meter's Reading
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        current_power = energy_meter_instance.current_power
        logging.info("time: " + current_time + " | " + "power: " + str(current_power))

        sql = "INSERT INTO " + "`" + _config['mysql']['table']['table_name'] + "`" + " (`" + _config['mysql']['table']['time_col'] + "`, `" + _config['mysql']['table']['power_col'] + "`) VALUES (%s, %s)"
        logging.debug("Generated SQL: " + sql)
        try:
            with _db_connection.cursor() as cursor:
            # Create a new record
                cursor.execute(sql, (current_time, current_power))
            # Commit to DB
            _db_connection.commit()
            logging.info("Commited to DB")
        except Exception as e:
            logging.error(e)

        time.sleep(_config['system']['sensing_interval'])


if __name__ == "__main__":
    main()