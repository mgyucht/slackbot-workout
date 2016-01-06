import nose

from slackbot_workout.configurators import InMemoryConfigurationProvider
from slackbot_workout.database import PostgresConnector
from slackbot_workout.user_settings import PostgresUserSettingsProvider, UserAlreadyExistsException, NoSuchUserException

def get_sample_config():
    return InMemoryConfigurationProvider({
        'dbname': 'travis_ci_test',
        'user_exercise_limit': 4,
        'user_settings': {
            'enabled': True,
            'tablename': 'user_settings_test'
        }
    })

class TestUserSettings(object):
    config = get_sample_config()
    connector = PostgresConnector(dbname=config.dbname())

    def teardown(self):
        def clear_table(cursor):
            cursor.execute("DELETE FROM {}".format(self.config.user_settings_tablename()))
        self.connector.with_connection(clear_table)

    @classmethod
    def teardown_class(self):
        def drop_table(cursor):
            cursor.execute("DROP TABLE {}".format(self.config.user_settings_tablename()))
        self.connector.with_connection(drop_table)

    def get_settings_provider(self):
        config = get_sample_config()
        connector = PostgresConnector(dbname=config.dbname())
        return PostgresUserSettingsProvider(connector, config)

    def test_add_user__not_exists(self):
        user_settings = self.get_settings_provider()
        user_settings.add_user('uid1')

    @nose.tools.raises(UserAlreadyExistsException)
    def test_add_user__exists(self):
        user_settings = self.get_settings_provider()
        user_settings.add_user('uid1')
        user_settings.add_user('uid1')

    def test_exercise_limit_for_user_exists(self):
        user_settings = self.get_settings_provider()
        user_settings.add_user('uid1')
        assert user_settings.exercise_limit_for_user('uid1') == 4

    @nose.tools.raises(NoSuchUserException)
    def test_exercise_limit_for_user__not_exists(self):
        user_settings = self.get_settings_provider()
        user_settings.exercise_limit_for_user('uid1')

    def test_set_exercise_limit_for_user(self):
        user_settings = self.get_settings_provider()
        user_settings.add_user('uid1')
        user_settings.set_exercise_limit_for_user('uid1', 8)
        assert user_settings.exercise_limit_for_user('uid1') == 8

