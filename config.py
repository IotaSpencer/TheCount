import json
import os.path
import sys
from logger import logger
import yaml as YAML
from box import Box

class Cfg:
    def __init__(self):
        try:
            self.bot_config = Box.from_yaml(filename=f"{os.path.expanduser('~')}/.countingv2/config.yml")
        except FileNotFoundError:
            logger.error('~/.countingv2/config.yml or parent directories does not exist! Exiting!')
            sys.exit(1)
        except YAML.YAMLError as e:
            logger.error(f"Error parsing YAML config: {e}")
            sys.exit(1)