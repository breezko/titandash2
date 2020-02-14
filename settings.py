import os
import pathlib
import shutil
import datetime
import logging

# APPLICATION VERSION.
VERSION = "0.0.1"

# Grabbing the directory that this file is in.
# Proves useful when dealing with files alongside
# the application itself.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# Grab the windows local users directory (ie: C://Users//<username>).
USER_DIR = str(pathlib.Path.home())
# Modules directory stores all references and files used in extension alongside
# the titandash application.
MODULES_DIR = os.path.join(PROJECT_DIR, "modules")
# Web directory is used by our eel application to determine
# where all of our static web files are kept.
WEB_DIR = os.path.join(PROJECT_DIR, "web")

# Base local data directory that's used to store all of our
# local data files in a reusable location.
LOCAL_DATA_DIR = os.path.join(USER_DIR, ".titandash2")
# Database directory will contain our database file that's used
# within the application.
LOCAL_DATA_DB_DIR = os.path.join(LOCAL_DATA_DIR, "database")
# Logging directory that will contain a copy of the most recent
# application logs.
LOCAL_DATA_LOG_DIR = os.path.join(LOCAL_DATA_DIR, "logging")
# An additional directory is available within the database
# directory that stores instances of database backups.
LOCAL_DATA_BACKUP_DIR = os.path.join(LOCAL_DATA_DB_DIR, "backups")


# Eel Constants.
EEL_WEB = "web"
EEL_LOGIN = "login.html"
EEL_HOME = "index.html"
EEL_JINJA_TEMPLATES = "templates"
EEL_INIT_OPTIONS = {
    'js_result_timeout': 10000
}
EEL_START_OPTIONS = {
    'mode': "chrome",                        # Defaulting to chrome browser.
    'port': 0,                               # Port: 0 will automatically pick one.
    'block': True,                           # Blocking start() call until finished.
    'jinja_templates': EEL_JINJA_TEMPLATES,  # String specifying folder to use for Jinja2 templates.
    'size': (1200, 800)                      # Tuple of ints specifying width and height of window.
}

# ORM Settings (SQLite).
DB_NAME = "titandash.db"
DB_FILE = os.path.join(LOCAL_DATA_DB_DIR, DB_NAME)

# Authenticator Settings.
AUTH_BASE_URL = "https://titandash.net"
AUTH_AUTH_URL = "{base}/{auth}".format(base=AUTH_BASE_URL, auth="auth")


def __user_directories():
    """
    Perform some idempotent functionality to create and generate the local
    data directories that are used by the application.

    We ensure that this function runs before any others, making sure that directories are
    always available where needed.
    """
    for path in [d for d in [LOCAL_DATA_DIR, LOCAL_DATA_DB_DIR, LOCAL_DATA_LOG_DIR, LOCAL_DATA_BACKUP_DIR] if not os.path.exists(d)]:
        os.makedirs(path)

    # At this point, we can be sure that the database data directories are at least present,
    # we will need to create the database file if it does not already exist.
    if not os.path.exists(DB_FILE):
        open(DB_FILE, "w")


def __backup_database(limit=10):
    """
    Perform required functionality to create database backups (pseudo lazily).

    We only attempt to backup the database when the settings file is imported somewhere. if a backup
    is not currently available for the current day, we create a new backup.
    """
    def create():
        """
        Create a new database backup file with the current date appended to the database name.
        """
        shutil.copyfile(
            src=DB_FILE,
            dst=os.path.join(LOCAL_DATA_BACKUP_DIR, "titandash_{date}.db".format(date=datetime.datetime.now().date().strftime("%Y-%m-%d")))
        )

    def backup_date(backup):
        """
        Given a backup file's name, parse out the date string from the filename.
        """
        return datetime.date(*[int(s) for s in backup.split("_")[1].split(".")[0].split("-")])

    # Grab all available backups first.
    backups = [backup for backup in os.listdir(LOCAL_DATA_BACKUP_DIR) if os.path.isfile(os.path.join(LOCAL_DATA_BACKUP_DIR, backup))]

    # No backups present yet. Let's just create one now.
    if len(backups) == 0:
        create()
    # Some backups are currently present, but the limit has not been hit yet.
    # Checking if one needs to be created based on the most recent backups date.
    elif len(backups) < limit:
        # If the current date is greater than the last available backup, generate
        # a brand new database backup file.
        if datetime.datetime.now().date() > backup_date(backup=backups[-1]):
            create()

            # New backup created, should we also remove a backup now that a new
            # one has been created?
            if len(backups) + 1 >= limit:
                os.remove(path=os.path.join(LOCAL_DATA_BACKUP_DIR, backups[0]))


__user_directories()
__backup_database()
