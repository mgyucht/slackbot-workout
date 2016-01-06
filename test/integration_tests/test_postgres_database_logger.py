from slackbot_workout.configurators import InMemoryConfigurationProvider
from slackbot_workout.database import PostgresConnector
from slackbot_workout.loggers import PostgresDatabaseLogger

def get_sample_config():
    return InMemoryConfigurationProvider({
        'dbname': 'travis_ci_test',
        'workout_log': {
            'tablename': 'workout_log'
        }
    })

class TestPostgresDatabaseLogger(object):
    config = get_sample_config()
    connector = PostgresConnector(dbname=config.dbname())

    def teardown(self):
        def clear_table(cursor):
            cursor.execute("DELETE FROM {}".format(self.config.workout_log_tablename()))
        self.connector.with_connection(clear_table)

    @classmethod
    def teardown_class(self):
        def drop_table(cursor):
            cursor.execute("DROP TABLE {}".format(self.config.workout_log_tablename()))
        self.connector.with_connection(drop_table)

    def get_logger(self):
        config = get_sample_config()
        connector = PostgresConnector(dbname=config.dbname())
        return PostgresDatabaseLogger(config, connector)

    def test_log_exercise(self):
        logger = self.get_logger()
        logger.log_exercise('miles', 'pushups', 30, 'reps')

        def get_exercises(cursor):
            cursor.execute("SELECT username, exercise, reps FROM {}".format(
                self.config.workout_log_tablename()))
            return cursor.fetchall()
        exercises = self.connector.with_connection(get_exercises)
        assert exercises == [('miles', 'pushups', 30)]

    def test_get_todays_exercises(self):
        logger = self.get_logger()
        logger.log_exercise('miles', 'pushups', 30, 'reps')
        logger.log_exercise('greg', 'situps', 40, 'reps')

        exercises = logger.get_todays_exercises()

        assert 'miles' in exercises
        assert exercises['miles'] == [{'exercise': 'pushups', 'reps': 30}]
        assert 'greg' in exercises
        assert exercises['greg'] == [{'exercise': 'situps', 'reps': 40}]
