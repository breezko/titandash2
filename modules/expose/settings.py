from settings import (
    VERSION, PROJECT_DIR, USER_DIR, MODULES_DIR, WEB_DIR, LOCAL_DATA_DIR,
    LOCAL_DATA_DB_DIR, LOCAL_DATA_LOG_DIR, LOCAL_DATA_BACKUP_DIR, EEL_WEB,
    EEL_JINJA_TEMPLATES, EEL_LOGIN, EEL_DASHBOARD, EEL_INIT_OPTIONS, EEL_START_OPTIONS,
    DB_NAME, DB_FILE, AUTH_BASE_URL, AUTH_AUTH_URL
)

import eel


@eel.expose
def settings_information():
    """
    Grab all settings information from the settings module.
    """
    return {
        "Version": VERSION,
        "Local Data Directory": LOCAL_DATA_DIR,
        "Local Data Database Directory": LOCAL_DATA_DB_DIR,
        "Local Data Log Directory": LOCAL_DATA_LOG_DIR,
        "Local Data Backup Directory": LOCAL_DATA_BACKUP_DIR,
        "Database Name": DB_NAME,
        "Database File": DB_FILE,
        "Authentication Base URL": AUTH_BASE_URL,
        "Authentication Auth URL": AUTH_AUTH_URL,
    }
