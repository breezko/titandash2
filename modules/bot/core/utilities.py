from settings import LOCAL_DATA_DIR, LOCAL_DATA_LOG_DIR

from modules.bot.core.exceptions import TransitionStateError

from string import Formatter

import datetime
import logging
import time
import eel


_format = "[%(asctime)s] %(levelname)s [{instance}] [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"


class EelHandler(logging.StreamHandler):
    """
    Custom handler used to ensure emitted logs are sent to the frontend.
    """
    def __init__(self, instance, stream=None):
        """
        Initialize the handler with the proper instance attached for use when emitted.
        """
        super(EelHandler, self).__init__(stream=stream)

        # Ensure instance is available as an instance
        # attribute, can be used later on.
        self.instance = instance

    def emit(self, record):
        """
        Emit function fired whenever a log is sent.
        """
        eel.base_log_emitted(self.instance.pk, self.format(record=record))


def bot_logger(instance, configuration):
    """
    Create a new bot logger with the instance specified.
    """
    def _generate_file_name(name):
        """
        Generate a log file name with the instance name and date attached.
        """
        return "{log_dir}/{name}.log".format(
            log_dir=LOCAL_DATA_LOG_DIR,
            name=name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        )

    formatter = logging.Formatter(_format.format(instance=instance.name))
    logger = logging.getLogger("titandash.{instance}".format(instance=instance.pk))

    # Return early if the logger in question already contains handlers.
    # Likely duplicate logger and no need to add more handlers.
    if logger.handlers:
        return logger

    _file_name = _generate_file_name(name=instance.slug())

    for handler in [logging.FileHandler(_file_name), logging.StreamHandler(), EelHandler(instance=instance)]:
        # Make sure the handler in question has the appropriate formatter and level set.
        handler.setLevel(configuration.logging_level)
        handler.setFormatter(formatter)
        # Add the handler to our logger object.
        logger.addHandler(handler)

    # Ensure we're using the proper logging level from configuration.
    logger.setLevel(configuration.logging_level)
    # Ensure we've disabled the logger if configuration specifies for it.
    logger.disabled = not configuration.enable_logging

    logger.debug("logger has been initialized.")
    logger.debug("logger file: {file}".format(file=_file_name))
    logger.debug("logger level: {level}".format(level=logger.level))
    logger.debug("logger name: {name}".format(name=logger.name))

    return logger


def format_string(string, lower=False):
    """
    Format a string object to a readable format.
    """
    _repl = string.replace("_", " ")

    # We can also determine whether or not the string should
    # be made to a lowercase format, or titled.
    return _repl.lower() if lower else _repl.title()


def format_delta(delta):
    """
    Format a timedelta object.
    """
    fmt = "{D}d {H}:{M}:{S}"
    f = Formatter()
    d = {}

    dct = {
        "D": 86400,
        "H": 3600,
        "M": 60,
        "S": 1,
    }

    k = map(lambda x: x[1], list(f.parse(format_string=fmt)))
    r = int(delta.total_seconds())

    for i in ("D", "H", "M", "S"):
        if i in k and i in dct.keys():
            d[i], r = divmod(r, dct[i])

    for key, value in d.items():
        if value < 10 and "D" not in key:
            d[key] = "0" + str(value)

    return f.format(fmt, **d)


def convert_to_number(value):
    """
    Attempt to convert the given value into a proper number value. Values may be (integer, float, string with unit).
    """
    try:
        # Maybe the value can just be coerced right into a float
        # value without any parsing.
        return float(value)
    except ValueError:
        # ValueError occurs when this value can't be made
        # into a float without parsing.
        pass

    # Attempt to parse out a unit from the value specified.
    # Values could contain a special unit at the end of the value.
    # ie: (100K, 10M, etc).
    unit = value[-1]

    if unit not in ["K", "M"]:
        # Unit found is not supported, go ahead and
        # raise a value error.
        raise ValueError("Unit found is not supported: {unit}".format(unit=value[-1]))

    try:
        # Try to coerce our value, without the unit included
        # into a number before converting with unit.
        number = float(value[:-1])
    except ValueError:
        # The number parsed is not supported at all.
        # Just error our with a useful message about why.
        raise("Number found is not valid: {number}".format(number=value[:-1]))

    # Finally, convert the number into the proper value
    # based on the unit parsed from the original value.
    return {"K": 10**3, "M": 10**6}[unit] * number


def delta_from_value_string(value):
    """
    Attempt to generate a delta from the given value string provided.
    """
    # Create a dictionary of base arguments for our delta
    # creation, this will allow us to use a values that may not have all
    # of the needed delta kwargs.
    _kwargs = {"days": 0, "hours": 0, "minutes": 0}
    _current = None

    try:
        for v in value:
            if v.endswith("d"):
                _current = "days"
            elif v.endswith("h"):
                _current = "hours"
            elif v.endswith("m"):
                _current = "minutes"

            if _current:
                _kwargs[_current] = int(v[:-1])

    # Catch any value errors that occur and just return
    # a none variable to use as the delta.
    except ValueError:
        return None

    _delta = datetime.timedelta(**_kwargs)

    # Return our delta if it represents a duration longer than
    # zero seconds, otherwise we return none similar to above.
    return _delta if _delta.total_seconds() > 0 else None


def in_transition_func(instance, max_loops):
    """
    Attempt to resolve transition state of the game's current state.
    """
    loops = 0

    while loops != max_loops:
        # Maybe the game has crashed, which means we're likely in the emulators
        # home screen, look for the app icon and try to open the game again.
        if instance.find_and_click(image=instance.images.generic_app_icon):
            # We did boot up the game... Wait a couple of seconds before
            # continuing to try and resolve the state.
            time.sleep(5)

        # Check for any early game or non vip game prompts
        # that may appear on the screen game load after being out of the game.
        instance.welcome_screen_check()
        instance.rate_screen_check()

        # Are any panels open that should probably be closed. The large exist panel image
        # should only be present when a larger panel is opened in game.
        instance.find_and_click(image=instance.images.generic_large_exit_panel, pause=0.5)
        # Is an ad panel open that might need to be accepted or declined.
        instance.collect_ad_no_transition()

        _valid_images = [
            instance.images.generic_exit_panel, instance.images.no_panel_clan_raid_ready, instance.images.no_panel_clan_no_raid,
            instance.images.no_panel_daily_reward, instance.images.no_panel_fight_boss, instance.images.no_panel_hatch_egg,
            instance.images.no_panel_leave_boss, instance.images.no_panel_settings, instance.images.no_panel_tournament,
            instance.images.no_panel_pet_damage, instance.images.no_panel_master_damage
        ]

        # Check the screen for any images that are only present when the game is in a valid
        # state when the check is performed. Safe to derive that we are not in a transition.
        if instance._search(image=_valid_images):
            return

        # Unable to resolve state at this point, attempt to click on the screen a couple
        # of times to try and close ro resolve the state manually.
        instance.click(point=instance.locations.master_screen_top, clicks=3, pause=0.5)
        # Log some information about the failed transition resolve,
        # trying again after waiting.
        instance.logger.info("transition state could not be resolved, waiting one second and trying again...")

        # Increment loops and wait slightly
        # before trying to resolve again.
        time.sleep(1)
        loops += 1

    # Transition state can not be resolved. We need to manually error our of this bot session.
    # Cleanup should be handled by the bot itself when exception is caught.
    raise TransitionStateError("transition state of game could not be resolved, exiting bot session now...")
