from modules.orm.models import User
from modules.auth.authenticator import Authenticator

import eel


@eel.expose
def load_remembered_information():
    """
    Attempt to grab the remembered information from the database and return the values.
    """
    if User.is_available():
        return User.grab().json

    # Otherwise, no user is currently available, we will return an none type
    # variable instead which can be used in our javascript.
    return None


@eel.expose
def login(username, token):
    """
    Attempt to log a user into the system. A username and token are expected and an authentication
    check should also take place to ensure that the user is valid and allowed to login.
    """
    user = User.grab(username=username, token=token).json

    # Let's check the authentication result to see if any errors should be returned.
    errors = []
    if not user["state"]["valid"]:
        errors.append({
            "type": "danger",
            "message": "Please enter a valid username and token."
        })
    # User is already online? Only one instance should be available
    # at a given time.
    if user["state"]["online"]:
        errors.append({
            "type": "danger",
            "message": "Your account is already signed in."
        })

    return errors


@eel.expose
def load_user_information():
    """
    Attempt to grab the information for the user from the authentication backend.
    """
    # Function should only ever be hit when we make it to the index
    # page after logging in our being logged in already.
    user = User.grab()

    # User could be none though, due to weird usage of the app,
    # or someone has their information modified while in the app.
    if not user.state["valid"]:
        return {
            "status": "INVALID",
        }

    # User is valid, let's grab their information and return it.
    return Authenticator.information(username=user.username, token=user.token)

