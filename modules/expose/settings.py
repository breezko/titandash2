from settings import (
    VERSION, MODULES_DIR, WEB_DIR, LOCAL_DATA_DIR, LOCAL_DATA_DB_DIR, LOCAL_DATA_LOG_DIR, LOCAL_DATA_BACKUP_DIR,
    DB_NAME, DB_FILE, AUTH_BASE_URL, AUTH_AUTH_URL, DEPENDENCIES_DIR, BOT_DIR, BOT_DATA_DIR,
    BOT_IMAGE_DIR, TESSERACT_DEPENDENCY_DIR, TESSERACT_DIR, TESSERACT_PATH
)

import eel


@eel.expose
def settings_information():
    """
    Grab all settings information from the settings module.
    """
    return {
        "version": VERSION,
        "modules_directory": MODULES_DIR,
        "web_directory": WEB_DIR,
        "dependencies_directory": DEPENDENCIES_DIR,
        "bot_directory": BOT_DIR,
        "bot_data_directory": BOT_DATA_DIR,
        "bot_image_directory": BOT_IMAGE_DIR,
        "local_data_directory": LOCAL_DATA_DIR,
        "local_data_database_directory": LOCAL_DATA_DB_DIR,
        "local_data_log_directory": LOCAL_DATA_LOG_DIR,
        "local_data_backup_directory": LOCAL_DATA_BACKUP_DIR,
        "database_name": DB_NAME,
        "database_file": DB_FILE,
        "authentication_base_url": AUTH_BASE_URL,
        "authentication_auth_url": AUTH_AUTH_URL,
        "tesseract_dependency_directory": TESSERACT_DEPENDENCY_DIR,
        "tesseract_directory": TESSERACT_DIR,
        "tesseract_path": TESSERACT_PATH,
    }
