from modules.bot.core.decorators import BotProperty

import eel


@eel.expose
def shortcuts_information():
    """
    Grab all shortcuts information.
    """
    dct = {}

    # Loop through all available bot properties that are
    # queueable through a shortcut function (keyboard).
    for prop in BotProperty.shortcuts():
        # Adding the properties base name to our dictionary
        # of information, formatting is handled client side.
        dct[prop["name"]] = prop["shortcut"].split("+")

    # Returning our dictionary once all shortcut based
    # properties are available.
    return dct
