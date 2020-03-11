

class DynamicAttributes(object):
    """
    Dynamic allocation of static variables into a class instance. Allowing for dot notation retrieval.
    """
    def __init__(self, attributes, logger):
        """
        Initialize a new dynamic attributes object, ensuring that we loop through all provided values, setting as we progress.
        """
        self.logger = logger

        # Begin looping through all attributes passed in and set up the dynamic
        # attributes available on the class.
        for key, value in attributes.items():
            # Value passed in is a dictionary, we can loop through
            # all values available in the dictionary and perform setters.
            if isinstance(value, dict):
                for _key, _value in value.items():
                    self._check_attribute(key=_key, value=_value)

            # A basic value is passed in here, just perform our
            # setter like normal.
            else:
                self._check_attribute(key=key, value=value)

    def _check_attribute(self, key, value):
        """
        Perform a check on the specified attribute key, raising an exception if an attribute with that key is already set.
        """
        if getattr(self, key, None):
            # Raising a value error so that duplicate keys don't overwrite each-other.
            # This ensures that we notice when duplicates are present and can change them.
            raise ValueError("dynamic attribute: '{attribute}' has already been set, perhaps a duplicate key? "
                             "setting this value again would overwrite the previously set attribute with "
                             "the same name.".format(attribute=key))

        # Otherwise, we can simply perform our setter and log some information
        # about the attribute being set.
        else:
            setattr(self, key, value)
            # Log the key -> value of the dynamic attribute
            # being set at this point.
            self.logger.debug("dynamic attribute: {attribute} = {value}".format(attribute=key, value=value))
