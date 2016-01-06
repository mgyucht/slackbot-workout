from abc import ABCMeta, abstractmethod
import csv
import datetime
import time

class BaseLogger(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def log_exercise(self, username, exercise, reps, units):
        pass

    @abstractmethod
    def get_todays_exercises(self):
        pass

class StdOutLogger(BaseLogger):
    def log_exercise(self, username, exercise, reps, units):
        print "%s %s %d %s" % (username, exercise, reps, units)

    def get_todays_exercises(self):
        # We aren't actually persisting this data, so return no exercises for anyone
        return {}

class CsvLogger(BaseLogger):
    format_string = "%Y%m%d"

    def __init__(self, debug=False):
        self.debug = debug

    def csv_filename(self):
        debugString = "_DEBUG" if self.debug else ""
        return "log" + time.strftime(self.format_string) + debugString + ".csv"

    def log_exercise(self, username, exercise, reps, units):
        with open(self.csv_filename(), 'a') as f:
            writer = csv.writer(f)
            writer.writerow([str(datetime.datetime.now()),username,exercise,reps,units])

    def get_todays_exercises(self):
        exercises = {}
        with open(self.csv_filename(), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                username = row[1]
                exercise_data = {
                    'exercise': row[2],
                    'reps': int(row[3])
                }
                try:
                    exercises[username].append(exercise_data)
                except:
                    exercises[username] = [exercise_data]
        return exercises

class PostgresDatabaseLogger(BaseLogger):
    def __init__(self, config, connector):
        self.config = config
        self.connector = connector
        self.maybe_create_table()

    def maybe_create_table(self):
        def create_table_command(cursor):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS {} (
                    username VARCHAR(100) NOT NULL,
                    exercise VARCHAR(100) NOT NULL,
                    reps INT NOT NULL,
                    units VARCHAR(50) NOT NULL,
                    time TIMESTAMP DEFAULT current_timestamp
                );
            """.format(self.config.workout_log_tablename()))
        self.connector.with_connection(create_table_command)

    def log_exercise(self, username, exercise, reps, units):
        def log_exercise_command(cursor):
            cursor.execute("""
                INSERT INTO {}
                    (username, exercise, reps, units)
                VALUES
                    (%s, %s, %s, %s);
            """.format(self.config.workout_log_tablename()), (username, exercise, reps, units))
        self.connector.with_connection(log_exercise_command)

    def get_todays_exercises(self):
        def get_todays_exercises_command(cursor):
            cursor.execute("""
                SELECT username, exercise, reps
                FROM {}
                WHERE date_trunc('day', time) = date_trunc('day', now())
            """.format(self.config.workout_log_tablename()))
            exercises = {}
            for row in cursor.fetchall():
                username = row[0]
                exercise_data = {
                    'exercise': row[1],
                    'reps': row[2]
                }
                try:
                    exercises[username].append(exercise_data)
                except:
                    exercises[username] = [exercise_data]
            return exercises

        return self.connector.with_connection(get_todays_exercises_command)
