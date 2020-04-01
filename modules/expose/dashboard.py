from db.models import BotInstance, Configuration, QueuedFunction
from db.utilities import play, resume, pause, stop

from modules.bot.core.window import WindowHandler
from modules.bot.core.decorators import BotProperty
from modules.bot.core.enumerations import State, Action

import eel


@eel.expose
def dashboard_add_instance():
    """
    Generate a new bot instance and return a dictionary with information about the new instance.
    """
    return BotInstance.objects.create().json()


@eel.expose
def dashboard_remove_instance(pk):
    """
    Remove the specified bot instance from the system.
    """
    BotInstance.objects.filter(pk=pk).delete()


@eel.expose
def dashboard_save_instance_name(pk, name):
    """
    Update the specified instance with a new name.
    """
    _instance = BotInstance.objects.get(pk=pk)
    _instance.name = name
    # Call save directly, ensuring that websockets will
    # be fired as intended.
    _instance.save()


@eel.expose
def dashboard_settings_information(selected_instance):
    """
    Retrieve available settings information, and the status of the currently selected instance.
    """
    # Grab all available windows present on the screen, additional filtering
    # can be performed below to place windows into dictionary values.
    _wh = WindowHandler(initial=True)
    _configurations = Configuration.objects.all()
    # Grab the specified instance (selected) or out one from the grab method. Since on initial page load,
    # a selected instance may not be ready, we can default to the first.
    _instance = BotInstance.objects.grab() if not selected_instance else BotInstance.objects.get(pk=selected_instance)

    return {
        "active": _instance.state in [State.RUNNING.value, State.PAUSED.value],
        "instance": {
            "configuration": _instance.configuration.pk if _instance.configuration else None,
            "window": _instance.window["hwnd"] if _instance.window else None
        },
        # Just grab the pk/name pair from configurations, grabbing all information
        # can be cumbersome for the system if many configurations are present.
        "configurations": [{"pk": configuration.pk, "name": configuration.name} for configuration in _configurations],
        "windows": {
            "filtered": [window.json() for window in _wh.filter().values()],
            "all": [window.json() for window in _wh.filter(filter_titles=False, ignore_smaller=False).values()]
        },
        "shortcuts": _instance.shortcuts is True  # `is True` to ensure we deal with `null` values.
    }


@eel.expose
def dashboard_actions_information(selected_instance):
    """
    Retrieve the current actions information for the selected instance.
    """
    _instance = BotInstance.objects.grab() if not selected_instance else BotInstance.objects.get(pk=selected_instance)

    # Instance may be active or not, but we can use the state to determine
    # what we need to actually do.
    return {
        "state": _instance.state
    }


@eel.expose
def dashboard_actions_kill(selected_instance):
    """
    Attempt to kill the selected instance if it's currently running.
    """
    _instance = BotInstance.objects.get(pk=selected_instance)
    _status = "warning"

    # Depending on the current state, we can attempt to stop
    # the instance, or just return early with status.
    if _instance.state in [State.RUNNING.value, State.PAUSED.value]:
        _instance.stop()
        _status = "success"

    # Otherwise, the instance isn't actually running or paused, no need
    # to attempt to kill the instance.
    return {"status": _status}


@eel.expose
def dashboard_actions_signal(selected_instance, configuration, window, shortcuts, action):
    """
    Perform the specified signal against the selected instance.
    """
    _instance = BotInstance.objects.get(pk=selected_instance)

    # Additionally, we can do some initial checks here to make sure
    # that a configuration and window are selected in the dashboard,
    # otherwise, we can send back a toast message.
    if action == Action.PLAY.value:
        if not configuration or not window:
            if not configuration:
                eel.base_generate_toast("Signal", "A <strong>configuration</strong> must be selected before starting an instance.", "danger")
            if not window:
                eel.base_generate_toast("Signal", "A <strong>window</strong> must be selected before starting an instance.", "danger")

            # Return early as well from here so no functionality
            # is executed at this point.
            return

        # Play action selected.
        # This can represent one of two options, we're either starting a new instance,
        # or we're resuming one that is already running.
        if _instance.state == State.PAUSED.value:
            # Paused, attempt to resume the instance.
            resume(instance=_instance)
        if _instance.state == State.STOPPED.value:
            # Stopped, attempt to start a new instance.
            play(instance=_instance, configuration=configuration, window=window, shortcuts=shortcuts)

    # Pause action selected.
    # Run the base pause utility.
    if action == Action.PAUSE.value:
        pause(instance=_instance)
    # Stop action selected.
    # Run the base stop utility.
    if action == Action.STOP.value:
        stop(instance=_instance)


@eel.expose
def dashboard_queue_function_information(selected_instance):
    """
    Retrieve all queueables that are present and available within the bot instance.
    """
    _instance = BotInstance.objects.grab() if not selected_instance else BotInstance.objects.get(pk=selected_instance)

    return {
        "queued": [function.json() for function in QueuedFunction.objects.filter(instance=_instance)],
        "queueables": BotProperty.all()
    }


@eel.expose
def dashboard_queue_function(selected_instance, function, duration, duration_type):
    """
    Queue up a function for the specified bot instance.
    """
    _instance = BotInstance.objects.get(pk=selected_instance)

    # Let's attempt to generate the queued function for this instance.
    # Frontend validation should handle any invalid values before reaching this point.
    QueuedFunction.objects.create(
        instance=_instance,
        function=function,
        duration=duration,
        duration_type=duration_type
    )


@eel.expose
def dashboard_queue_function_flush(selected_instance):
    """
    Attempt to flush the queue available and remove all queued functions for an instance.
    """
    _instance = BotInstance.objects.get(pk=selected_instance)
    _index = 0

    # Filter on all available queued functions for the instance,
    # deleting each one and sending a signal to remove it from the
    # frontend completely.
    for _index, queued in enumerate(QueuedFunction.objects.filter(instance=_instance), start=1):
        # Remove will properly delete the queued function
        # and send a signal to the frontend to remove it from our table.
        queued.remove()

    _message = "Flushed <strong>{index}</strong> function(s) scheduled to execute against <em>{instance}</em>".format(
        index=_index,
        instance=_instance.name
    )
    # Send a message to frontend about our flushed functions.
    # Letting the user know how many were removed and that flushing is done.
    eel.base_generate_toast("Flush Queue", _message, "success")


@eel.expose
def dashboard_instance_information(selected_instance):
    """
    Retrieve the information the instance specified.
    """
    _instance = BotInstance.objects.grab() if not selected_instance else BotInstance.objects.get(pk=selected_instance)

    # Return all the json information that's associated with this instance.
    # Allowing us to display initial information where needed.
    return _instance.json()