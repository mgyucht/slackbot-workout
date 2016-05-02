from abc import ABCMeta, abstractmethod
import json
import os
import yaml

from .constants import Constants
from .exercise import from_dict
from .util import InvalidLoggerTypeException
from future.utils import with_metaclass

class ConfigurationProvider(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def load_configuration(self):
        pass

    @abstractmethod
    def load_exercise(self, filename):
        pass

    def set_configuration(self):
        self.config = self.load_configuration()
        if hasattr(self, 'exercise_list'):
            del self.exercise_list

    def get_config_or_default(self, default, option_path):
        sub_config = self.config
        try:
            for option in option_path:
                sub_config = sub_config[option]
            return sub_config
        except:
            return default

    def channel_name(self):
        return self.config['channel_name']

    def bot_name(self):
        return self.config['bot_name']

    def webserver_port(self):
        return self.get_config_or_default(80, ['webserver_port'])

    def slack_token(self):
        return self.config['slack_token']

    def office_hours_on(self):
        return self.get_config_or_default(False, ['office_hours', 'on'])

    def office_hours_begin(self):
        return self.config['office_hours']['begin']

    def office_hours_end(self):
        return self.config['office_hours']['end']

    def debug(self):
        return self.get_config_or_default(False, ['debug'])

    def min_time_between_callouts(self):
        return self.get_config_or_default(17, ['callouts', 'time_between', 'min_time'])

    def max_time_between_callouts(self):
        return self.get_config_or_default(23, ['callouts', 'time_between', 'max_time'])

    def num_people_per_callout(self):
        return self.get_config_or_default(3, ['callouts', 'num_people'])

    def group_callout_chance(self):
        return self.get_config_or_default(0.05, ['callouts', 'group_callout_chance'])

    def exercise_directory(self):
        return self.get_config_or_default('exercises', ['exercise_directory'])

    def exercises(self):
        if not hasattr(self, 'exercise_list'):
            self.exercise_list = self.load_exercises()
        return self.exercise_list

    def load_exercises(self):
        """
        Loads exercises from the exercise directory.
        """
        exercise_list = []
        for dirname, _, filenames in os.walk(self.exercise_directory()):
            for filename in filenames:
                fname = os.path.join(dirname, filename)
                if fname.endswith(".yaml"):
                    exercise = self.load_exercise(fname)
                    exercise_list.append(exercise)
        return exercise_list

    def user_exercise_limit(self):
        return self.get_config_or_default(3, ['user_exercise_limit'])

    def enable_acknowledgment(self):
        return self.get_config_or_default(False, ['enable_acknowledgment'])

    def workout_logger_type(self):
        log_type = self.get_config_or_default(Constants.IN_MEMORY_LOGGER, ['workout_logger_type'])
        if log_type in Constants.LOGGER_CLASSES:
            return log_type
        else:
            raise InvalidLoggerTypeException(log_type)

    def workout_logger_settings(self):
        return self.get_config_or_default(None, ['workout_logger_settings'])

    def aggregate_exercises(self):
        return self.get_config_or_default(False, ['aggregate_exercises'])

class GenericConfigurationProvider(ConfigurationProvider):
    def __init__(self, config_name, config_type, config_source):
        assert config_type in Constants.CONFIGURATIONS, \
               "config_type must be either yaml or json"
        assert config_source in Constants.CONFIGURATION_SOURCES, \
               "config_source must be env, file, or in_memory"
        self.config_name = config_name
        self.config_type = config_type
        self.config_source = config_source
        self.set_configuration()

    def load_configuration(self):
        if self.config_source == Constants.CONFIGURATION_SOURCE_FILE:
            with open(self.config_name, "r") as f:
                raw_config = f.read()
        elif self.config_source == Constants.CONFIGURATION_SOURCE_ENV:
            raw_config = os.environ[self.config_name]
        return self.add_creds(self.cook_config(raw_config))

    def add_creds(self, cooked_config):
        SECRET_PATH = "/flexbot/secrets"
        with open(SECRET_PATH + "/username", "r") as f:
            cooked_config["workout_logger_settings"]["user"] = f.read()
        with open(SECRET_PATH + "/password", "r") as f:
            cooked_config["workout_logger_settings"]["password"] = f.read()
        return cooked_config

    def cook_config(self, raw_config):
        if self.config_type == Constants.CONFIGURATION_YAML:
            return yaml.load(raw_config)
        elif self.config_type == Constants.CONFIGURATION_JSON:
            return json.loads(raw_config)

    def load_file(self, filename):
        with open(filename, "r") as f:
            return self.cook_config(f.read())

    def load_exercise(self, filename):
        return from_dict(self.load_file(filename))

class InMemoryConfigurationProvider(ConfigurationProvider):
    def __init__(self, configuration, exercises=[]):
        self.configuration = configuration
        self.provided_exercise_list = exercises
        self.set_configuration()

    def update_configuration(self, updates):
        self.configuration.update(updates)

    def load_configuration(self):
        return self.configuration

    def load_exercises(self):
        return self.provided_exercise_list

    def load_exercise(self, filename):
        pass
