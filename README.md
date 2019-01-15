# WemoEnergyLogger
This program fetches data from [Wemo® Insight Smart Plug](https://www.belkin.com/us/p/P-F7C029/) in *local network*, formats data and transfer data to TIPPERS service using REST API. It uses the APIs from library: [GitHub - iancmcc/ouimeaux: Python API to Belkin WeMo devices](https://github.com/iancmcc/ouimeaux) and UpnP protocol to discover Wemo plugs and get data from them. Please refer to ouimeaux’s source code and library if you would like to know the details of the protocol. 

After installing all needed libs, simply run `python energy_logger.py ` to execute the program.

