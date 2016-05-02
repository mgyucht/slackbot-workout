from . import loggers

class Constants(object):
    ACKNOWLEDGE_SUCCEEDED = 0
    ACKNOWLEDGE_FAILED = 1
    ACKNOWLEDGE_DISABLED = 2

    IN_MEMORY_LOGGER = loggers.InMemoryLogger.__name__
    CSV_LOGGER = loggers.CsvLogger.__name__
    POSTGRES_DATABASE_LOGGER = loggers.PostgresDatabaseLogger.__name__

    LOGGER_CLASSES = [
        IN_MEMORY_LOGGER,
        CSV_LOGGER,
        POSTGRES_DATABASE_LOGGER
    ]

    CONFIGURATION_YAML = "yaml"
    CONFIGURATION_JSON = "json"

    CONFIGURATIONS = [
        CONFIGURATION_YAML,
        CONFIGURATION_JSON
    ]

    CONFIGURATION_SOURCE_ENV = "env"
    CONFIGURATION_SOURCE_FILE = "file"

    CONFIGURATION_SOURCES = [
        CONFIGURATION_SOURCE_ENV,
        CONFIGURATION_SOURCE_FILE
    ]
