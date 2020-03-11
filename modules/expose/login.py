from db.models import User

import eel


@eel.expose
def login_load_remembered_information():
    """
    Attempt to grab the remembered information from the database and return the values.
    """
    if User.objects.available():
        return User.objects.grab().json

    # Otherwise, no user is currently available, we will return an none type
    # variable instead which can be used in our javascript.
    return None


@eel.expose
def login(username, token):
    """
    Attempt to log a user into the system. A username and token are expected and an authentication
    check should also take place to ensure that the user is valid and allowed to login.
    """
    user = User.objects.grab(username=username, token=token).json

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
