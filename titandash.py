from settings import EEL_WEB, EEL_LOGIN, EEL_HOME, EEL_INIT_OPTIONS, EEL_START_OPTIONS

from modules.expose.functions import *
from modules.orm.models import User

import eel


class TitandashApplication(object):
    """
    TitandashApplication.

    Encapsulating all functionality required to boot-up the titanbot application. We're mostly looking to encapsulate the
    initialize functionality that will derive whether or not a user has already logged in or not, allowing us to skip
    the login page, and go directly to the bot startup section.

    None of the explicit Eel functionality should be present here for exposing, but rather handled in a different module
    and called directly from there as needed.
    """
    def __init__(self):
        """
        Initialize application.
        """
        # Initializing application through Eel module.
        # "EEL_WEB" represents our "web" folder, which contains all web server specific files.
        eel.init(path=EEL_WEB, **EEL_INIT_OPTIONS)

    @staticmethod
    def start():
        """
        Attempting to "start" and open the application on the derived "page" (html file).
        """
        if User.is_valid():
            _url = EEL_HOME
        # If no user is currently in the database, or one is, but their account
        # is no longer valid, send the user to the login page.
        else:
            _url = EEL_LOGIN

        eel.start(_url, **EEL_START_OPTIONS)


if __name__ == "__main__":
    TitandashApplication().start()
