import argparse
import json
import logging
import logging.config
import os
import yaml

from flexbot.configurators import GenericConfigurationProvider
from flexbot.constants import Constants
from flexbot.server import Server

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.yaml",
            help="Configuration file path (can be JSON or YAML)")
    parser.add_argument("-l", "--logging-config", default="logging.yaml",
            help="Logging configuration file path (can be JSON or YAML)")
    args = parser.parse_args()

    if args.logging_config.startswith("env:"):
        env_name = args.logging_config.split("env:")[1]
        if env_name.endswith("YAML"):
            logging_config = yaml.load(os.environ[env_name])
        elif env_name.endswith("JSON"):
            logging_config = json.loads(os.environ[env_name])
        else:
            raise Exception("Environment name {} must end with YAML or JSON".format(env_name))
        logging.config.dictConfig(logging_config)
    else:
        with open(args.logging_config, 'r') as f:
            if args.logging_config.endswith(".yaml"):
                logging.config.dictConfig(yaml.load(f))
            elif args.logging_config.endswith(".json"):
                logging.config.dictConfig(json.load(f))
            else:
                raise Exception("Logging configuration path must end with .yaml or .json")

    config_source = Constants.CONFIGURATION_SOURCE_FILE
    config_name = args.config
    if args.config.startswith("env:"):
        config_source = Constants.CONFIGURATION_SOURCE_ENV
        config_name = args.config.split("env:")[1]
        if config_name.endswith("YAML"):
            config_type = Constants.CONFIGURATION_YAML
        elif config_name.endswith("JSON"):
            config_type = Constants.CONFIGURATION_JSON
        else:
            raise Exception("Environment name {} must end with YAML or JSON".format(env_name))
    elif config_name.endswith(".yaml"):
        config_type = Constants.CONFIGURATION_YAML
    elif config_name.endswith(".json"):
        config_type = Constants.CONFIGURATION_JSON
    else:
        raise Exception("Configuration path must end with .yaml or .json")
    config = GenericConfigurationProvider(config_name, config_type, config_source)

    server = Server(config)
    server.start()

if __name__ == "__main__":
    main()
