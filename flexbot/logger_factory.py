from .constants import Constants
from . import loggers

class LoggerFactory(object):
    def __init__(self, configuration):
        self.configuration = configuration

    def get_logger(self):
        logger_type = self.configuration.workout_logger_type()
        if logger_type == Constants.IN_MEMORY_LOGGER:
            return self.get_in_memory_logger()
        elif logger_type == Constants.CSV_LOGGER:
            return self.get_csv_logger()
        elif logger_type == Constants.POSTGRES_DATABASE_LOGGER:
            return self.get_postgres_database_logger()
        else:
            raise Exception("Unsupported logger type {}".format(logger_type))

    def get_in_memory_logger(self):
        return loggers.InMemoryLogger()

    def get_csv_logger(self):
        return loggers.CsvLogger()

    def get_postgres_database_logger(self):
        dbsettings = self.configuration.workout_logger_settings()
        tablename = dbsettings['tablename']
        winners_table = dbsettings['winners_table']
        del dbsettings['tablename']
        del dbsettings['winners_table']
        return loggers.PostgresDatabaseLogger(tablename, winners_table, **dbsettings)
