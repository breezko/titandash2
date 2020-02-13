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
        Attempt to authenticate the specified user.

        # TODO: Use proper authentication backend to test these values.
                Values returned here should determine whether or not
                the user is "valid".
        """
        return {
            "valid": True,
            "valid_username": True,
            "valid_token": True,
            "online": False,
            "license": {},
        }
