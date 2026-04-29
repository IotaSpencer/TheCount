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
        try:
            self.count_config = Box.from_json(filename=f"{os.path.expanduser('~')}/.countingbotv2/count.json")
        except FileNotFoundError:
            logger.warn('~/.countingbotv2/count.json does not exist, using default values')
            count_config = {
                "Step": 1,
                "StartingNumber": 0,
                "EnableWolframAlpha": False,
                "EnableBinary": True,
                "EnableExpressions": True,
                "RoundAllGuesses": False,
                "AllowSingleUserCount": False,
                "ForceIntegerConversions": True
            }
        except json.JSONDecodeError:
            logger.warn('failed to decode json')