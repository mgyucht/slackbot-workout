from setuptools import setup, find_packages
setup(
    name = "slackbot-workout",
    version = "0.1",
    packages = find_packages(),

    install_requires = [
        'requests==2.7.0',
        'psycopg2>=2.6.1'
    ],

    author = "Miles Yucht",
    author_email = "mgyucht@gmail.com",
    description = "A fun framework for incorporating more exercise into your life at work through Slack.",
    license = "MIT",
    keywords = "slack slackbot exercise"
)