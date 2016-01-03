from nose.tools import assert_raises

from slackbot_workout.configurators import InMemoryConfigurationProvider

class TestConfig(object):
    def test_options_with_default(self):
        config = InMemoryConfigurationProvider({})
        assert config.webserver_port() == 80
        assert config.office_hours_on() == False
        assert config.debug() == False
        assert config.min_time_between_callouts() == 17
        assert config.max_time_between_callouts() == 23
        assert config.group_callout_chance() == 0.05
        assert config.user_exercise_limit() == 3

    def test_required_options(self):
        config = InMemoryConfigurationProvider({})
        assert_raises(KeyError, config.channel_name)
        assert_raises(KeyError, config.bot_name)
        assert_raises(KeyError, config.office_hours_begin)
        assert_raises(KeyError, config.office_hours_end)
        assert_raises(KeyError, config.exercises)
