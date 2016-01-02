import cherrypy
import logging

class FlexbotWebServer(object):
    def __init__(self, user_manager, configuration):
        self.user_manager = user_manager
        self.configuration = configuration
        self.load_configuration()
        self.logger = logging.getLogger(__name__)

    def load_configuration(self):
        config_json = self.configuration.get_configuration()
        self.bot_name = config_json['botName']
        self.channel_name = config_json['channelName']
        self.exercises = config_json['exercises']

    @cherrypy.expose
    def index(self):
        self.load_configuration()
        return "Welcome to {}'s webserver!".format(self.bot_name)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def flex(self, **args):
        self.load_configuration()
        user_id = args['user_id']
        text = args['text'].lower()
        if user_id != "USLACKBOT" and self.bot_name.lower() in text:
            return self.handle_message(text)

    def handle_message(self, text):
        if "help" in text:
            return self.print_help()
        elif "exercises" in text:
            return self.print_exercises()
        elif "info" in text:
            return self.print_exercise_info(text)
        else:
            return self.print_stats(text)

    def print_help(self):
        helptext = """\
Welcome to {channel_name}! I am {bot_name}, your friendly helpful workout bot. Here are a couple useful commands you can use to talk with me:
- `{bot_name} help`: print this help message
- `{bot_name} exercises`: print the exercises that I can announce
- `{bot_name} info <EXERCISE>`: print a short informational blob on how to do `EXERCISE` correctly
- `{bot_name} user1 [user2 [...]]`: print the stats for user1, user2, ...
- `{bot_name} channel`: print the stats for everyone in the channel
- `{bot_name}, I don't have to listen to you`: doubles your exercise quota permanently (coming soon)
""".format(channel_name=self.channel_name, bot_name=self.bot_name)
        return {'text': helptext}

    def print_exercises(self):
        exercises_text = "The currently supported exercises are: "
        exercises_text += ", ".join(map(lambda e: e['name'], self.exercises))
        return {'text': exercises_text}

    def print_exercise_info(self, text):
        exercise_reverse_lookup = {}
        exercises_to_print = []
        for exercise in self.exercises:
            exercise_reverse_lookup[exercise['name']] = exercise
        for word in text:
            if word in exercise_reverse_lookup:
                exercises_to_print.append(exercise_reverse_lookup[word])
        if len(exercises_to_print) > 0:
            exercise_infos = []
            for exercise in exercises_to_print:
                exercise_info = "{} description: {}".format(exercise['name'], exercise['info'])
                exercise_infos.append(exercise_info)
            exercise_info_text = "\n".join(exercise_infos)
            return {'text': exercise_info_text}
        else:
            return {'text': 'You need to give me an exercise!'}

    def print_stats(self, text):
        words = text.split()
        user_reverse_lookup = {}
        users_to_print = []
        for user_id in self.user_manager.users:
            user = self.user_manager.users[user_id]
            user_reverse_lookup[user.username.lower()] = user_id
            user_reverse_lookup[user.real_name.lower()] = user_id
        for word in words:
            if word in user_reverse_lookup:
                users_to_print.append(user_reverse_lookup[word])
            elif word == "channel" or word == "@channel":
                users_to_print = self.user_manager.users.keys()
                break
        if len(users_to_print) > 0:
            stats = self.user_manager.stats(list(set(users_to_print)))
            self.logger.info("""\
            vvvvvvvvvvvvvvvvvvvvvvvv
            responding:
            {}
            ^^^^^^^^^^^^^^^^^^^^^^^^""".format(stats))
            return {
                "text": stats
            }


