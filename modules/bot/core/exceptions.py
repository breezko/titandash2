

class TransitionStateError(Exception):
    """
    Custom exception to specify errors that have occurred while attempting to resolve transition states.
    """
    pass


class TerminationEncountered(Exception):
    """
    Custom exception to raise an exception when a termination has been encountered by a bot.
    """
    pass


class ServerTerminationEncountered(Exception):
    """
    Custom exception to raise an exception when a server termination has been encountered by a bot.
    """
    pass


class FailsafeException(Exception):
    """
    Custom exception to catch a failsafe when the users mouse pointer is within a failsafe point.
    """
    pass


class WindowNotFoundError(Exception):
    """
    Custom exception that may be thrown when a specified hwnd is not found in a window handler.
    """
    pass
