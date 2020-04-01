from modules.bot.core.exceptions import FailsafeException

from pyautogui import failSafeCheck, FailSafeException as PyAutoGuiFailsafeException

from cachetools import TTLCache


# Create our caching object that will persist objects
# within memory for five seconds, we can make use of this
# with our globals wrapper to ensure database queries aren't
# constantly taking place when performing clicks or intensive functions.
_cache = TTLCache(maxsize=10, ttl=5)


class Globals(object):
    """
    Dynamic global configuration checker to retrieve global values with cached timeout for updates.
    """
    def __init__(self):
        """
        Initialize globals checker.
        """
        self._cache_key = "GLOBALS"

    @staticmethod
    def _get_globals():
        """
        Retrieve a fresh instance of the global configuration model.
        """
        # Local level import of the global configuration model.
        # Avoid circular import issues with model.
        from db.models import GlobalConfiguration

        # Grab the current global configuration object.
        # Acting as a (singleton).
        return GlobalConfiguration.objects.grab()

    def _set_cache(self, value):
        """
        Set our cache key to the specified value.
        """
        _cache[self._cache_key] = value

        # Let's also return the last cached value
        # for use after caching.
        return value

    def _get_cache(self):
        """
        Retrieve the cached instance of our global configuration, or retrieve a fresh instance from the database.
        """
        try:
            return _cache[self._cache_key]
        except KeyError:
            return self._set_cache(value=self._get_globals())

    def failsafe_enabled(self):
        """
        Return whether or not failsafe functionality is enabled.
        """
        return self._get_cache().enable_failsafe

    def failsafe_check(self):
        """
        Perform a failsafe check if failsafe functionality is currently enabled.
        """
        if self.failsafe_enabled():
            # Only actually performing a proper failsafe check
            # when enabled through the global configuration.
            try:
                failSafeCheck()
            except PyAutoGuiFailsafeException:
                # Catch the normal failsafe exception and raise our own
                # so it's easier to deal with conditional checks and exception info.
                raise FailsafeException()

    def game_event_enabled(self):
        """
        Return whether or not a game event is currently enabled.
        """
        return self._get_cache().enable_game_event

    def pihole_enabled(self):
        """
        Return whether or not pi-hole functionality is enabled.
        """
        return self._get_cache().enable_pihole
