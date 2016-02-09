import json
import logging

from .constants import Constants
from .user import User
from .util import NoEligibleUsersException

class UserManager(object):
    def __init__(self, api, configuration, workout_logger):
        self.api = api
        self.configuration = configuration
        self.workout_logger = workout_logger
        self.logger = logging.getLogger(__name__)

    def stats(self, user_list=[]):
        # Write to the command console today's breakdown
        s = "Today's stats:\n"
        s += "```\n"
        #s += "Username\tAssigned\tComplete\tPercent
        headerline = "Username".ljust(15)
        exercises = self.configuration.exercises()
        for exercise in exercises:
            headerline += exercise.name + "  "
        headerline += "Todo  "
        headerline += "Total\n"
        s += headerline
        s += "-" * len(headerline) + "\n"

        users = user_list if len(user_list) > 0 else self.fetch_users().values()
        for user in users:
            s += user.username.ljust(15)
            for exercise in exercises:
                s += str(self.exercise_count_for_user(user.user_id, exercise)).ljust(len(exercise.name) + 2)
            s += str(self.pending_exercises_for_user(user.user_id)).ljust(6)
            s += str(self.total_exercises_for_user(user.user_id))
            s += "\n"

        s += "```"
        return s

    # --------------------------------------
    # Fetching users from the channel
    # --------------------------------------

    def fetch_users(self):
        """
        Fetches all users in the channel
        """
        users = {}

        for user_id in self.api.get_members():
            user = self.get_user(user_id)
            self.logger.debug("Adding user {}".format(user))
            users[user_id] = user
        return users

    def fetch_active_users(self):
        """
        Returns a list of all active users in the channel
        """
        users = self.fetch_users()
        active_users = []
        for user_id in users:
            if self.api.is_active(user_id):
                active_users.append(user_id)
        return active_users

    # --------------------------------------
    # Acknowledgment mode methods
    # --------------------------------------

    def get_current_winners(self):
        return self.workout_logger.get_current_winners()

    def mark_winner(self, user_id, exercise, exercise_reps):
        if self.configuration.enable_acknowledgment():
            self.workout_logger.add_exercise(user_id, exercise, exercise_reps)
        else:
            self.add_exercise_for_user(user_id, exercise, exercise_reps)

    def acknowledge_winner(self, user_id):
        if self.configuration.enable_acknowledgment():
            exercise_data = self.workout_logger.finish_exercise(user_id)
            if exercise_data == None:
                return Constants.ACKNOWLEDGE_FAILED
            else:
                exercise = self.get_exercise_by_name(exercise_data['exercise'])
                self.add_exercise_for_user(user_id, exercise, exercise_data['reps'])
                return Constants.ACKNOWLEDGE_SUCCEEDED
        else:
            return Constants.ACKNOWLEDGE_DISABLED

    # --------------------------------------
    # User utility methods
    # --------------------------------------

    def get_user(self, user_id):
        return self.api.get_user_info(user_id)

    def get_firstname(self, user_id):
        try:
            return self.get_user(user_id).firstname
        except:
            return None

    def get_username(self, user_id):
        try:
            return self.get_user(user_id).username
        except:
            return None

    def get_mention(self, user_id):
        try:
            return self.get_user(user_id).get_mention()
        except:
            return None

    # --------------------------------------
    # Exercise utility methods
    # --------------------------------------

    def get_exercise_by_name(self, exercise_name):
        exercises = self.configuration.exercises()
        for exercise in exercises:
            if exercise.name == exercise_name:
                return exercise
        return None

    # --------------------------------------
    # Exercise management
    # --------------------------------------

    def get_eligible_users(self):
        """
        Get the current eligible users; throws NoEligibleUsersException if there are none. These are
        users who are online and have not yet completed their maximum daily limit of exercises.
        """
        active_users = self.fetch_active_users()

        winner_ids = list(self.get_current_winners().keys())
        eligible_users = []
        for user_id in active_users:
            total_exercises = self.total_exercises_for_user(user_id)
            if self.configuration.aggregate_exercises():
                total_exercises += self.pending_exercises_for_user(user_id)
            if total_exercises < self.configuration.user_exercise_limit():
                # If the user has not completed all exercises for the day, we add them if the
                # aggregate_exercises flag is set, or if they haven't yet been assigned an exercise.
                if user_id not in winner_ids or self.configuration.aggregate_exercises():
                    self.logger.info("Adding %s to eligible_users list", self.get_username(user_id))
                    eligible_users.append(user_id)

        if len(eligible_users) == 0:
            raise NoEligibleUsersException()

        return eligible_users

    def total_exercises_for_user(self, user_id):
        return len(self.workout_logger.get_todays_exercises().get(user_id, []))

    def pending_exercises_for_user(self, user_id):
        return len(self.get_current_winners().get(user_id, []))

    def exercise_count_for_user(self, user_id, exercise):
        exercises = self.workout_logger.get_todays_exercises()
        try:
            filtered_exercises = [e for e in exercises[user_id] if e['exercise'] == exercise.name]
            return len(filtered_exercises)
        except KeyError:
            return 0

    def user_has_done_exercise(self, user_id, exercise):
        return self.exercise_count_for_user(user_id, exercise) > 0

    def add_exercise_for_user(self, user_id, exercise, exercise_reps):
        self.logger.debug("User {} completed {} {} of {}".format(user_id, exercise_reps, exercise.units,
            exercise.name))
        self.workout_logger.log_exercise(user_id, exercise, exercise_reps)

