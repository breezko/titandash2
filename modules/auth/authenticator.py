import json


class Authenticator(object):
    """
    Encapsulate all the functionality used to authenticate users against an external backend system.
    """
    @staticmethod
    def get_state(username, token):
        """
        Attempt to authenticate the specified username and token.
        """
        return {
            "valid": True,
            "online": False,
            "license": {},
        }

    @staticmethod
    def online(instance):
        """
        Send a signal to the authentication backend, with information about the instance that's being set to online.
        """
        return True

    @staticmethod
    def offline(instance):
        """
        Send a signal to the authentication backend, with information about the instance that's being set to offline.
        """
        return True
