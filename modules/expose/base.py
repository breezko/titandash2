from settings import VERSION

from db.models import User, BotInstance

import eel


@eel.expose
def base_instances_available():
    """
    Grab all instances available currently.
    """
    return [
        instance.json() for instance in BotInstance.objects.all()
    ]


@eel.expose
def base_information():
    """
    Attempt to grab all of the base information present within the application.
    """
    data = {
        "app": {
            "version": VERSION
        },
    }

    # Grabbing the user if available and using our information,
    # otherwise, return a None value for user.
    if User.objects.available():
        data["user"] = User.objects.grab().json
    else:
        data["user"] = None

    return data
