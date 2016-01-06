from abc import ABCMeta, abstractmethod
import json
import os
import yaml

class TokenProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_user_token(self):
        pass

class EnvironmentTokenProvider(TokenProvider):
    def get_user_token(self):
        return os.environ['SLACK_USER_TOKEN_STRING']

class InMemoryTokenProvider(TokenProvider):
    def __init__(self, user_token):
        self.user_token = user_token

    def get_user_token(self):
        return self.user_token

class ConfigurationProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def load_configuration(self):
        pass

    def set_configuration(self):
        self.config = self.load_configuration()

    def get_config_or_default(self, default, option_path):
        sub_config = self.config
        try:
            for option in option_path:
                sub_config = sub_config[option]
            return sub_config
        except:
            return default

    # Slack configuration
    def channel_name(self):
        return self.config['channel_name']

    def bot_name(self):
        return self.config['bot_name']

    # Webserver configuration
    def webserver_port(self):
        return self.get_config_or_default(80, ['webserver_port'])

    # Bot behavior
    def min_time_between_callouts(self):
        return self.get_config_or_default(17, ['callouts', 'time_between', 'min_time'])

    def max_time_between_callouts(self):
        return self.get_config_or_default(23, ['callouts', 'time_between', 'max_time'])

    def num_people_per_callout(self):
        return self.get_config_or_default(3, ['callouts', 'num_people'])

    def group_callout_chance(self):
        return self.get_config_or_default(0.05, ['callouts', 'group_callout_chance'])

    def exercises(self):
        return self.config['exercises']

    # Max exercises per user per day
    def user_exercise_limit(self):
        return self.get_config_or_default(3, ['user_exercise_limit'])

    # Database logging configuration
    def dbname(self):
        return self.get_config_or_default('flexecution', ['dbname'])

    def workout_log_tablename(self):
        return self.get_config_or_default('flexecution', ['workout_log', 'tablename'])

    # Print extra debugging information, and short sleeps in places
    def debug(self):
        return self.get_config_or_default(False, ['debug'])

    # Configurable options
    # Office hours
    def office_hours_on(self):
        return self.get_config_or_default(False, ['office_hours', 'on'])

    def office_hours_begin(self):
        return self.config['office_hours']['begin']

    def office_hours_end(self):
        return self.config['office_hours']['end']

    # Per-user settings configuration
    def user_settings_enabled(self):
        return self.get_config_or_default(False, ['user_settings', 'enable'])

    def user_settings_tablename(self):
        return self.get_config_or_default('user_settings', ['user_settings', 'tablename'])

    # Enable acknowledgment
    def enable_acknowledgment(self):
        return self.get_config_or_default(False, ['enable_acknowledgment'])

class JsonFileConfigurationProvider(ConfigurationProvider):
    def __init__(self, filename):
        self.filename = filename
        self.set_configuration()

    def load_configuration(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

class YamlFileConfigurationProvider(ConfigurationProvider):
    def __init__(self, filename):
        self.filename = filename
        self.set_configuration()

    def load_configuration(self):
        with open(self.filename, 'r') as f:
            return yaml.load(f)

class InMemoryConfigurationProvider(ConfigurationProvider):
    def __init__(self, configuration):
        self.configuration = configuration
        self.set_configuration()

    def update_configuration(self, updates):
        self.configuration.update(updates)

    def load_configuration(self):
        return self.configuration

