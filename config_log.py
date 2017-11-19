import logging
import json
import logging.config


def config_logger():
    """Configures logging per the settings in logger_config.json
    """
    path = 'logger_config.json'
    try:
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    except FileNotFoundError:
        print("Make sure logger_config.json present")
        exit

config_logger()
