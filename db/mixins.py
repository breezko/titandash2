

class ExportModelMixin(object):
    """
    Encapsulate any of the general functionality used to export models into shareable formatted strings.
    """
    GENERIC_BLACKLIST = [
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
    ]

    M2M_SEPARATOR = "|"
    ATTRIBUTE_SEPARATOR = "&"
    VALUE_SEPARATOR = ":"
    BOOLEAN_PREFIX = "+B"
    M2M_PREFIX = "+M"
    FK_PREFIX = "+F"

    @staticmethod
    def import_model_kwargs(export_string, compression_keys=None):
        """
        Generate the keyword arguments for a model that's going to be imported.
        """
        raise NotImplementedError()

    @staticmethod
    def import_model(export_kwargs):
        """
        Importing a model directly into the database through this function.
        """
        raise NotImplementedError()

    def export_key(self):
        """
        Retrieve a key for usage with our export models, allows us to avoid primary key issues being different during imports.
        """
        raise NotImplementedError()

    def export_model(self, compression_keys=None, blacklist=None):
        """
        Export the model int a formatted string of values that can be imported back into the system.
        """
        # Set out keyword argument to empty dictionary and list values
        # if the user has not specified any directly.
        if compression_keys is None:
            compression_keys = {}
        if blacklist is None:
            blacklist = {}

        _attributes = []

        # Looping through all fields on the model that aren't one to many fields,
        # or fields that are present in our generic blacklist.
        for field in [f for f in self._meta.get_fields() if not f.one_to_many and f.name not in self.GENERIC_BLACKLIST or f.name not in blacklist]:
            # Grabbing the value of our field, and the compression key being used by
            # the model for each field available.
            _field_value = getattr(self, field.name)
            _compress_key = compression_keys.get(field.name, field.name)

            # We also need to determine what kind of field is being compressed, based on this,
            # we can use the proper prefix and separators.

            # A many to one relational field is being used,
            # use our foreign key prefix value.
            if field.many_to_one:
                value = "{prefix}{value}".format(prefix=self.FK_PREFIX, value=_field_value.export_key())

            # Maybe a many to many field is being used,
            # use our many to many prefix and separator values.
            elif field.many_to_many:
                # A many to many field will require is to check whether or not
                # any values are actually selected for the field.
                _m2m_value = [val.export_key() for val in _field_value.all()]

                # Use a none describer for this many to many, or grab the export
                # key for each model present on the field.
                value = "{prefix}{value}".format(
                    prefix=self.M2M_PREFIX,
                    value="None" if not _m2m_value else self.M2M_SEPARATOR.join([val.export_key() for val in _m2m_value])
                )

            # Otherwise, a basic field is being used currently,
            # we can just go ahead and use a boolean or value separator.
            else:
                # Boolean field being used, make sure we use the proper
                # proper boolean separator.
                if _field_value in [True, False]:
                    # Only using the "T/F" from the boolean found.
                    # Make sure to coerce and use [0] index.
                    value = "{prefix}{value}".format(prefix=self.BOOLEAN_PREFIX, value=str(_field_value)[0])
                else:
                    # Default field and value, just use whatever the
                    # field value is currently set to.
                    value = _field_value

            # Add this attribute our total list of attributes.
            _attributes.append(
                "{name}{separator}{value}".format(
                    name=_compress_key,
                    separator=self.VALUE_SEPARATOR,
                    value=value
                )
            )

        # All attributes are collected and available, let's go ahead
        # and compress them all into a single string output.
        return self.ATTRIBUTE_SEPARATOR.join(_attributes)
