# Create a tuple of base fields that we can safely use to use proper
# super calls within our properties class.
__base__ = ("fields", "instance", "logger")


class Properties(object):
    """
    Dynamic property container used to encapsulate the ability to set values on our instance and also perform a save call.
    """
    def __init__(self, instance, logger):
        """
        Set up the instance and build out the list of valid properties.
        """
        # Import bot instance locally,
        # avoid circular import issues.
        from db.models import BotInstance

        self.fields = [field.name for field in BotInstance._meta.get_fields() if not field.name.startswith("_")]
        self.instance = instance

        # Setup initialized logger and ensure we log some debugging information
        # to display all properties that are available.
        self.logger = logger
        self.logger.debug("properties initialized: {properties}".format(properties=", ".join(self.fields)))

    def __getattr__(self, item):
        """
        Retrieve values from our base fields, or from our defined fields variable on the instance.
        """
        if item in __base__:
            # Item being grabbed is one of our base fields.
            # We can use our super call to just grab this without issue.
            return super(Properties, self).__getattribute__(item)
        if item in self.fields:
            # Item is present in our list of available instance fields.
            # we can grab the item right off of our instance model.
            _value = getattr(self.instance, item)
            # Log debugging information about property retrieved.
            self.logger.debug("property: {item} retrieved: {value}".format(item=item, value=_value))
            # Return proper value after retrieving and logging.
            return _value

    def __setattr__(self, key, value):
        """
        Set the specified key value on our properties instance.
        """
        if key in __base__:
            # Key being set is one of our base fields.
            # We use our super call to set the value directly on our properties instance.
            super(Properties, self).__setattr__(key, value)
        if key in self.fields:
            # Setting the instance value directly. This ensures that socket
            # signals will fire with the proper data.
            setattr(self.instance, key, value)
            # Log debugging information about property set.
            self.logger.debug("property: {key} set: {value}".format(key=key, value=value))
            # Calling save on the instance handles the actual firing of our
            # websocket signal.
            self.instance.save()
