from abc import ABCMeta, abstractmethod
import psycopg2
import psycopg2.errorcodes

class UserSettingsProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_user(self, user_id):
        pass

    @abstractmethod
    def exercise_limit_for_user(self, user_id):
        pass

    @abstractmethod
    def set_exercise_limit_for_user(self, user_id):
        pass

class UserAlreadyExistsException(Exception):
    def __init__(self, user_id):
        self.user_id = user_id

    def __str__(self):
        return "User with id {} already exists".format(self.user_id)

class NoSuchUserException(Exception):
    def __init__(self, user_id):
        self.user_id = user_id

    def __str__(self):
        return "User with id {} does not exist".format(self.user_id)

class PostgresUserSettingsProvider(UserSettingsProvider):
    def __init__(self, connector, config):
        self.connector = connector
        self.config = config
        self.maybe_create_table()

    def maybe_create_table(self):
        def maybe_create_table_command(cursor):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS {} (
                    user_id VARCHAR(20) PRIMARY KEY,
                    exercise_limit INT NOT NULL
                )
            """.format(self.config.user_settings_tablename()))
        self.connector.with_connection(maybe_create_table_command)

    def add_user(self, user_id):
        def add_user_command(cursor):
            try:
                cursor.execute("""
                    INSERT INTO {}
                        (user_id, exercise_limit)
                    VALUES
                        (%s, %s)
                    """.format(self.config.user_settings_tablename()),
                    (user_id, self.config.user_exercise_limit()))
            except psycopg2.Error as e:
                if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                    raise UserAlreadyExistsException(user_id)
        self.connector.with_connection(add_user_command)

    def exercise_limit_for_user(self, user_id):
        def exercise_limit_for_user_command(cursor):
            cursor.execute("""
                SELECT exercise_limit
                FROM {}
                WHERE user_id = %s
            """.format(self.config.user_settings_tablename()), (user_id,))
            if cursor.rowcount == 0:
                raise NoSuchUserException(user_id)
            result = cursor.fetchone()
            return result[0]
        return self.connector.with_connection(exercise_limit_for_user_command)

    def set_exercise_limit_for_user(self, user_id, new_limit):
        def set_exercise_limit_for_user_command(cursor):
            cursor.execute("""
                UPDATE {}
                SET exercise_limit = %s
                WHERE user_id = %s
            """.format(self.config.user_settings_tablename()), (new_limit, user_id))
            if cursor.rowcount == 0:
                raise NoSuchUserException(user_id)
        self.connector.with_connection(set_exercise_limit_for_user_command)
