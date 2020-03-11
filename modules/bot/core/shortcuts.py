from modules.bot.core.decorators import BotProperty
from modules.bot.core.enumerations import Shortcut

import collections
import keyboard
import operator
import datetime


class Shortcuts(object):
    """
    Keyboard shortcuts functionality encapsulation.
    """
    def __init__(self):
        """
        Initialize shortcuts module, setting up default variables.
        """
        self._function_shortcuts = {}
        self._shortcut_functions = {}

        self._hooked = False

        self._loggers = []
        self._instances = []
        self._cooldown = 1

        self._timestamp = datetime.datetime.now()
        self._resume = datetime.datetime.now()

        self._current = {}
        self._index = 0

    def _regenerate_current(self):
        """
        Attempt to regenerate the dictionary of "current" selected keyboard buttons into a valid combo string.
        """
        return "+".join(
            # Generate an ordered dictionary of the current items and each key associated,
            # returning as keys() to support iterable requirement of join() call.
            collections.OrderedDict(sorted(self._current.items(), key=operator.itemgetter(1))).keys()
        )

    def _execute(self, combo, function):
        """
        Attempt to execute the combo/function pair. Queueing and logging as needed.
        """
        # Local level import of the queued function
        # model, avoid circular importing with module.
        from db.models import QueuedFunction

        for _instance, _logger in zip(self._instances, self._loggers):
            # Queue up the function being executed and ensure
            # we log some information about the combo execution.
            QueuedFunction.objects.create(instance=_instance, function=function)
            _logger.info("shortcut: {combo} pressed, adding function: {function} to queue.".format(combo=combo, function=function))

        # Updating the resume value used
        # to allow for small wait periods in between executions.
        self._resume += datetime.timedelta(seconds=self._cooldown)

    @staticmethod
    def _fix_event(event):
        """
        Fix an event so that any of the shift, ctrl, or alt buttons can be used to initiate a combo.
        """
        _split = event.name.split(" ")[-1]

        # If the split event derived is any of our available
        # shortcut enumeration values, we can use that as our
        # event, allowing for left shift, right shift, etc.
        if _split in [s.value for s in Shortcut]:
            return _split

        # Just return the event name otherwise.
        return event.name

    def _on_press(self, event):
        """
        Perform functionality whenever a keyboard button is pressed.
        """
        self._timestamp = datetime.datetime.now()

        # Make sure to fix up our index if it's fallen
        # below the allowed threshold.
        if self._index < 0:
            self._index = 0

        # An event is available, fix the event and attempt to parse
        # the available functions from the key pressed and update
        # the module to support multiple keys pressed at once.
        if event:
            _key = self._fix_event(event=event)
            # If the key grabbed is already in our "current" set
            # of pressed characters, go ahead and return early.
            if _key in self._current:
                return

            # Determine if the key pressed is present in any of the available shortcuts
            # present within the module.
            for _shortcut in self._function_shortcuts:
                # Split on the separator for shortcuts (+),
                # so we can support combos.
                if _key in _shortcut.split("+"):
                    # Update our "current" and "index" values
                    # to notify of a successful add of a keypress.
                    self._current[_key] = self._index
                    self._index += 1
                    break

            if len(self._current) > 0:
                # The "current" dictionary contains multiple elements (or a single combo piece),
                # regenerate the combo and see if we can queue up and log the shortcut being executed.
                _combo = self._regenerate_current()
                _func = self._function_shortcuts.get(_combo)

                # Valid function could be grabbed through combo and available
                # function shortcuts. Begin queueing up and logging the execution.
                if _func:
                    if self._timestamp > self._resume:
                        # Execute should handle the queueing, logging and timestamp
                        # updates that are required.
                        self._execute(combo=_combo, function=_func)

    def _on_release(self, event):
        """
        Perform functionality whenever a keyboard button is released.
        """
        try:
            # Popping the current event out of our current dictionary.
            # Lower the index by one to account for this change.
            self._current.pop(self._fix_event(event=event))
            self._index -= 1
        except KeyError:
            # Just pass on key error.
            # Released a key that isn't present.
            pass

    def add_handler(self, instance, logger):
        """
        Add a new handler to the shortcuts module.
        """
        self._instances.append(instance)
        self._loggers.append(logger)

        # Log some information about this new shortcuts handler
        # that's been added to the module.
        logger.info("instance: {instance} has been added to the shortcuts module successfully.".format(instance=instance.name))

    def clear_handlers(self):
        """
        Clear all handlers currently present within the shortcuts module.
        """
        self._instances.clear()
        self._loggers.clear()

    def hook(self):
        """
        Hook the keyboard "on_press" and "on_release" functionality with custom module functionality.
        """
        if not self._hooked:
            # Hook hasn't taken place yet, setup shortcut / function maps
            # at a module level once so all possibilities are accounted for.
            for prop in BotProperty.shortcuts():
                # Assign properties to self instance variables.
                self._function_shortcuts[prop["shortcut"]] = prop["name"]
                self._shortcut_functions[prop["name"]] = prop["shortcut"]

            keyboard.on_press(callback=self._on_press)
            keyboard.on_press(callback=self._on_release)

            # Flipping the hooked flag now, hook will be called every time
            # an instance is being started with shortcuts enabled, but functionality
            # will only occur once.
            self._hooked = True

    def unhook(self, instance, logger):
        """
        Unhook the specific instance and logger from the shortcuts module.
        """
        if instance in self._instances:
            # Remove the specified instance from the list
            # of available instances in the module.
            self._instances.remove(instance)
        if logger in self._loggers:
            # Remove the specified logger from the list
            # of available loggers in the module.
            self._loggers.remove(logger)

        # Debug some information about the unhooked
        # instance and logger.
        logger.debug("instance: {instance} has been unhooked successfully.".format(instance=instance))


# Create an instance of the shortcuts object
# that can be used throughout the application.
shortcuts_handler = Shortcuts()
