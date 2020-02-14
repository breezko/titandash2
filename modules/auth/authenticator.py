import json


class Authenticator(object):
    """
    Authenticator.

    Encapsulating the functionality used to authenticate users with an external system.

    Users should be able to login with their email address and authentication token.
    """
    @staticmethod
    def authenticate(username, token):
        """
        Attempt to authenticate the specified username and token.
        """
        return {
            "valid": True,
            "online": False,
            "license": {},
        }

    @staticmethod
    def information(username, token):
        """
        Attempt to retrieve the user information for the specified user and their token.
        """
        return {
            "configurations": []
        }
