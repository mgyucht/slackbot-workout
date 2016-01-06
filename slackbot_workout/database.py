from abc import ABCMeta, abstractmethod
import logging
import psycopg2

class DatabaseConnector(object):
    __metaclasss__ = ABCMeta

    @abstractmethod
    def with_connection(self, func):
        pass

class PostgresConnector(DatabaseConnector):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.kwargs = kwargs

    def with_connection(self, func):
        conn = None
        try:
            conn = psycopg2.connect(**self.kwargs)
            cursor = conn.cursor()
            self.logger.debug("precursor")
            result = func(cursor)
            conn.commit()
            self.logger.debug("committed")
            return result
        except psycopg2.Error:
            self.logger.exception("Failure during database connection")
            conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

