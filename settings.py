import os
import pathlib
import shutil
import datetime

# APPLICATION VERSION.
VERSION = "0.0.1"
# GAME VERSION.
VERSION_GAME = "3.7.1"
# GAME VERSION VARIABLES.
MAX_STAGE = 92000

# Create an active flag that can be checked in other modules
# to determine the state of our server currently. While running,
# we will know by seeing that _active = True. Eel's close callback
# will ensure we set this to False as soon as the server is terminated.
_active = False


def get_active_state():
    """
    Retrieve the current active state value.
    """
    # _active -> globally available.
    global _active
    # Just return the current _active flag state.
    return _active


def set_active_state(state):
    """
    Set the current active state value.
    """
    # _active -> globally available.
    global _active
    # Set the current _active flag state
    # to the specified value.
    _active = state


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
# Dependencies directory used to store all external dependencies used
# by the application to determine where these executables or data files reside.
DEPENDENCIES_DIR = os.path.join(PROJECT_DIR, "dependencies")
# Bot directory stores all bot specific references and files.
# The most important one being our images directory.
BOT_DIR = os.path.join(MODULES_DIR, "bot")
# The bot data directory can be used to store things like
# images and resources used by the bot that do not change.
BOT_DATA_DIR = os.path.join(BOT_DIR, "data")
# The bot images data directory should be used to store
# all images that the bot uses to search for and click on things.
BOT_IMAGE_DIR = os.path.join(BOT_DATA_DIR, "images")
# Place any exposed images here, images that could be displayed
# on the dashboard or frontend should be placed here.
WEB_IMAGE_DIR = os.path.join(WEB_DIR, "images")
# Artifact images are stored in a slightly different location,
# they're placed within the web folder so we can expose them on the frontend.
ARTIFACT_IMAGE_DIR = os.path.join(WEB_IMAGE_DIR, "artifacts")

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

# Eel Static Web Directory.
EEL_WEB = "web"
# Eel Templates Directory.
EEL_JINJA_TEMPLATES = "templates"
# Eel Login Template.
EEL_LOGIN = "{templates}/{login}".format(templates=EEL_JINJA_TEMPLATES, login="login.html")
# Eel Dashboard Template.
EEL_DASHBOARD = "{templates}/dashboard/{dashboard}".format(templates=EEL_JINJA_TEMPLATES, dashboard="dashboard.html")
# Initialize options for the eel init call.
EEL_INIT_OPTIONS = {
    'js_result_timeout': 10000
}
# Initialize options for the eel start call.
EEL_START_OPTIONS = {
    'mode': "chrome",                        # Defaulting to chrome browser.
    'port': 0,                               # Port: 0 will automatically pick one.
    'block': True,                           # Blocking start() call until finished.
    'jinja_templates': EEL_JINJA_TEMPLATES,  # String specifying folder to use for Jinja2 templates.
    'size': (700, 900)                      # Tuple of ints specifying width and height of window.
}

# Database Settings (SQLite) - Django ORM.
DB_NAME = "titandash.sqlite3"
DB_FILE = os.path.join(LOCAL_DATA_DB_DIR, DB_NAME)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_FILE
    }
}

# Setting up an installed app so that our database directory
# acts as it should when interacting with Django.
INSTALLED_APPS = (
    "db",
)

SECRET_KEY = "titan*vhl)__8$t#g@tkh$-==3c9^o!3v=tg_ic93yl2v3ykcxq&v@_dash"

# Authenticator Settings.
AUTH_BASE_URL = "https://titandash.net"
AUTH_AUTH_URL = "{base}/{auth}".format(base=AUTH_BASE_URL, auth="auth")

# Tesseract (Dependency) Settings.
TESSERACT_DEPENDENCY_DIR = os.path.join(DEPENDENCIES_DIR, "tesseract")
TESSERACT_DIR = os.path.join(TESSERACT_DEPENDENCY_DIR, "Tesseract-OCR")
TESSERACT_PATH = os.path.join(TESSERACT_DIR, "tesseract.exe")

# Bot Specific Settings.
DATETIME_FORMAT = "%m/%d/%Y %I:%M:%S %p"


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
