import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Project Directories.
# --------------------
MODULES_DIR = os.path.join(PROJECT_DIR, "modules")
REQUIREMENTS_DIR = os.path.join(PROJECT_DIR, "requirements")
WEB_DIR = os.path.join(PROJECT_DIR, "web")

# Eel Constants.
# --------------
EEL_WEB = "web"
EEL_LOGIN = "login.html"
EEL_HOME = "index.html"
EEL_INIT_OPTIONS = {
    'js_result_timeout': 10000
}
EEL_START_OPTIONS = {
    'mode': "chrome",   # Defaulting to chrome browser.
    'port': 0,          # Port: 0 will automatically pick one.
    'block': True,      # Blocking start() call until finished.
    'size': (600, 700)  # Tuple of ints specifying width and height of window.
}

# Project Files.
# --------------
# Requirements Files.
REQUIREMENTS_FILE = os.path.join(REQUIREMENTS_DIR, "requirements.txt")

# ORM Settings (SQLite).
DB_NAME = "titandash.db"
DB_FILE = os.path.join(PROJECT_DIR, DB_NAME)

# Authenticator Settings.
AUTH_BASE_URL = "https://titandash.net"
AUTH_AUTH_URL = "{base}/{auth}".format(base=AUTH_BASE_URL, auth="auth")
