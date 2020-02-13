from modules.orm.models import User

import eel


@eel.expose
def load_remembered_information():
    """
    Attempt to grab the remembered information from the database and return the values.
    """
    if User.is_available():
        return User.get().json

    # Otherwise, no user is currently available, we will return an none type
    # variable instead which can be used in our javascript.
    return None


@eel.expose
def login(username, token):
    """
    Attempt to log a user into the system. A username and token are expected and an authentication
    check should also take place to ensure that the user is valid and allowed to login.
    """
    errors = []
    user = User.grab(username=username, token=token)



    print(user)






