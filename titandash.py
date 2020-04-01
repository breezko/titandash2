from settings import (
    EEL_WEB, EEL_INIT_OPTIONS, EEL_START_OPTIONS, EEL_LOGIN, EEL_DASHBOARD,
)

from logger import application_logger

import os
import eel
import sys
import django

# Make sure our environment variable is set when
# application is booted up.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Attempt to setup Django modules and plugins
# on initial entry point once.
django.setup()

# Import all Django models that will be used by the main application
# entry point, any accessing of models elsewhere should not need to do this.
from db.models import User

# Let's also import our eel functions and expose them globally,
# regardless of them being used here or not.
import modules.expose


logger = application_logger()


def close_callback(*args, **kwargs):
    """
    Initiate specific functionality whenever a websocket is closed by eel.
    """
    # Sleeping for one second, and checking if any websockets
    # are available again.
    eel.sleep(1)

    # If any websockets are available, we know that the server
    # is not being shutdown.
    if len(eel._websockets) == 0:
        # Local level import of application state.
        # Avoiding circular imports.
        from db.models import ApplicationState

        logger.info("exiting application now.")

        # Set our active state to the proper value. Using database level
        # value to ensure different processes can read this value.
        ApplicationState.objects.set(state=False)
        sys.exit()


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
        logger.info("initializing titandash application with options: '{options}'".format(options={"path": EEL_WEB, **EEL_INIT_OPTIONS}))
        # Initializing application through Eel module.
        # "EEL_WEB" represents our "web" folder, which contains all web server specific files.
        eel.init(path=EEL_WEB, **EEL_INIT_OPTIONS)

    @staticmethod
    def start():
        """
        Attempting to "start" and open the application on the derived "page" (html file).
        """
        # Import any local level utilities that may be used
        # before the web-server is initialized.
        from django.core.management import call_command
        from db.models import ApplicationState
        from db.utilities import generate_models

        # Run the migrate command within django.
        # Making sure our models are upto date.
        call_command(command_name="migrate", app="titandash")

        # Server is being started, it is safe for us
        # to update our active flag.
        ApplicationState.objects.set(state=True)

        # Generate any initial models that we expect
        # to be available by default.
        generate_models()

        _url = EEL_DASHBOARD if User.objects.valid() else EEL_LOGIN

        logger.info("starting titandash application with options: '{options}'".format(options={"path": _url, **EEL_START_OPTIONS}))
        # Start eel, providing our start url defined above, the close callback
        # to deal with cleanup functionality, and default options.
        eel.start(_url, close_callback=close_callback, **EEL_START_OPTIONS)


if __name__ == "__main__":
    # Generate a create an instance of the titandash application.
    # Running until terminated by closing the window or exiting thread.
    TitandashApplication().start()
