from settings import DB_FILE

from modules.auth.authenticator import Authenticator

from peewee import SqliteDatabase, Model, CharField, BooleanField, DoesNotExist

import json


_db = SqliteDatabase(database=DB_FILE)


class BaseModel(Model):
    """
    Base model for any database models used by the titanbot application.
    """
    class Meta:
        database = _db


class User(BaseModel):
    """
    User model intent on storing the last entered information regarding a user attempting to login to the system.
    """
    username = CharField()
    token = CharField()
    state_json = CharField()

    @classmethod
    def is_available(cls):
        """
        Return whether or not a single user exists in the system yet ot not.
        """
        try:
            return isinstance(cls.get(), User)
        except DoesNotExist:
            return False

    @classmethod
    def is_valid(cls):
        """
        Return whether or not a user is valid by checking that a user is available, and that an existing account is valid.
        """
        if cls.is_available():
            # A user is available, let's check the current validation state
            # available for them, making sure that they are still valid.
            return cls.grab().state["valid"]

        # No user is available at all, invalid information present.
        return False

    @classmethod
    def grab(cls, username=None, token=None, user=None):
        """
        Attempt to grab the current user account and update it to reflect the specified email and token.
        """
        if not username and not token and not user:
            user = cls.get_or_none()
        if user:
            username = user.username
            token = user.token

        # Username and token should be specified when calling function, unless
        # an explicit user object is passed in to perform a "refresh" of sorts.
        if not username or not token:
            raise ValueError("Username, Token are required args, unless a user is passed into function.")

        data_dict = {
            "username": username,
            "token": token,
            "state_json": json.dumps(Authenticator.authenticate(username=username, token=token))
        }

        if not cls.is_available():
            cls.create(**data_dict)
        # An account does currently exists, we can grab it and update the values before
        # attempting to validate or authenticate the user.
        else:
            cls.get().update(**data_dict).execute()

        return cls.get()

    @property
    def state(self):
        """
        Attempt to return the current users state json as a python dictionary.
        """
        return json.loads(self.state_json)

    @property
    def json(self):
        """
        Return a json compliant dictionary with user information.
        """
        return {
            "username": self.username,
            "token": self.token,
            "state": self.state
        }


_db.connect()
_db.create_tables(models=[User])
