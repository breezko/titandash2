from settings import LOCAL_DATA_DIR

import logging


_format_base = "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"


def application_logger():
    """
    Generate and return a globally available application logger.
    """
    formatter = logging.Formatter(_format_base)
    logger = logging.getLogger("titandash")

    # Return early if the logger in question (our global logger) already contains handlers.
    # Likely duplicate logger no need to re-add handlers.
    if logger.handlers:
        return logger

    handler = logging.FileHandler("{dir}/{name}.log".format(dir=LOCAL_DATA_DIR, name="titandash"), mode="w")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.debug("logger has been initialized.")
    logger.debug("logger name: {name}".format(name=logger.name))

    return logger
