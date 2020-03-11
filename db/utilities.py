from db.mixins import ExportModelMixin

from modules.bot.core.bot import Bot
from modules.bot.core.window import WindowHandler
from modules.bot.core.enumerations import State

import threading
import time
import eel


def generate_url(model, key):
    """
    Generate a url that may be used by any pages that should load dynamic information based on specific model data.
    """
    return "{host}:{port}/templates/{model}?pk={key}".format(
        host=eel._start_args["host"],
        port=eel._start_args["port"],
        model=model._meta.model_name,
        key=key
    )


def play(instance, configuration, window, shortcuts):
    """
    Attempt to initiate a new bot. (Play).
    """
    # Avoid circular imports of models.
    from db.models import QueuedFunction, Configuration

    # If the instance state is currently already running, or paused,
    # which shouldn't happen based on thr way the UI works, but better
    # safe than sorry here.
    if instance.state in [State.RUNNING.value, State.PAUSED]:
        # Queue up an explicit termination of the running bot.
        QueuedFunction.objects.create(instance=instance, function="terminate")

    # Wait until the instance has been terminated properly in the backend.
    # Refreshing the instance instance each time.
    while not instance.is_stopped():
        # Loop forever until the instance is correctly in a stopped state.
        time.sleep(0.1)

    # Initialize a new thread to run our bot within.
    # Options present must be valid (through GUI).
    threading.Thread(
        target=Bot,
        kwargs={
            "instance": instance,
            "configuration": Configuration.objects.get(pk=configuration),
            "window": WindowHandler().grab(hwnd=window),
            "shortcuts": shortcuts,
            "run": True
        }
    ).start()


def stop(instance):
    """
    Send a stop signal to the selected instance.
    """
    # Avoid circular imports.
    from db.models import QueuedFunction

    if instance.state == State.STOPPED.value:
        # Return early if the bot is already in a proper stopped state.
        return

    # Otherwise, add an explicit "terminate" function to the instances queue.
    QueuedFunction.objects.create(instance=instance, function="terminate")


def pause(instance):
    """
    Send a pause signal to the selected instance.
    """
    # Avoid circular imports.
    from db.models import QueuedFunction

    if instance.state == State.STOPPED.value:
        # Return early if the bot is already in a proper stopped state.
        return

    # Otherwise, add an explicit "pause" function to the instances queue.
    QueuedFunction.objects.create(instance=instance, function="pause")


def resume(instance):
    """
    Send a resume signal the selected instance.
    """
    # Avoid circular imports.
    from db.models import QueuedFunction

    if instance.state == State.STOPPED.value:
        # Return early if the bot is already in a proper stopped state.
        return

    # Otherwise, add an explicit "resume" function to the instances queue.
    QueuedFunction.objects.create(instance=instance, function="resume")


def import_model_kwargs(export_string, compression_keys=None):
    """
    Generate the import model kwargs that are used to generate a new configuration instance through an import.
    """
    _kwargs = {}

    # Begin by parsing out the export string provided,
    # we need to make sure we remove leading or trailing whitespace.
    _string = export_string.strip()
    _attributes = _string.split(ExportModelMixin.ATTRIBUTE_SEPARATOR)

    for _attribute in _attributes:
        # Loop through each attribute available from the export string,
        # Make sure we have the key and value for each attribute.
        key, value = _attribute.split(ExportModelMixin.VALUE_SEPARATOR)

        # If a compression key is being used, make sure we convert to
        # the proper attribute name.
        if compression_keys:
            # Attempt to grab compression key "actual" value,
            # fall back to our default key if we can not find it.
            key = compression_keys.get(key, key)

        # At this point, the key should be the name of an attribute on the model
        # being imported, since a non compression key value should just be using the
        # attribute name anyways.

        if value.startswith(ExportModelMixin.BOOLEAN_PREFIX) and value.endswith("T") or value.endswith("F"):
            # Boolean value found, set value to proper
            # boolean type.
            value = value[-1] == "T"

        elif value.startswith(ExportModelMixin.FK_PREFIX):
            # Foreign key value found, remove the prefix and attempt
            # to grab the value for the foreign key.
            value = value[value.index(ExportModelMixin.FK_PREFIX) + len(ExportModelMixin.FK_PREFIX):]

            # Make sure we set our value to a none variable if no foreign
            # key was specified for this value.
            if value == "None":
                value = None

        elif value.startswith(ExportModelMixin.M2M_PREFIX):
            # Many to many key value found, remove the prefix and attempt
            # to grab all values for the many to many relation.
            value = value[value.index(ExportModelMixin.M2M_PREFIX) + len(ExportModelMixin.M2M_PREFIX):]

            # Loop through all available selected many to many values.
            # Using our many to many separator to split.
            value = [_value for _value in value.split(ExportModelMixin.M2M_SEPARATOR)]

            # Make sure we set our values to none variables if any
            # of them are set to proper none values.
            for _index, _value in enumerate(value):
                if _value == "None":
                    value[_index] = None

        else:
            # Otherwise, we've encountered a field without any proper parsing done to it.
            # can simply just treat it as a plain integer value or character value.
            try:
                # Try to coerce to integer, if this fails, just attempt
                # to make the value into a none type value or use the value itself.
                value = int(value)
            except ValueError:
                # Just use the string representation as long as the value
                # is not just a basic none value.
                value = value if value != "None" else None

        _kwargs[key] = value

    # Return our import kwargs after parsing
    # has been complete on all available values.
    return _kwargs


def generate_models():
    """
    Generate any high level models that expect default to be available.
    """
    # Import any of our required models locally within this functions
    # scope so that we do not pollute other locations that may import
    # other database utility functions.
    from db.models import BotInstance, Artifact, Configuration

    BotInstance.objects.ensure_defaults()
    Artifact.objects.ensure_defaults()
    Configuration.objects.ensure_defaults()
