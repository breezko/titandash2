from enum import Enum


class BotEnum(Enum):
    """
    Base Bot Enumeration.
    """
    @classmethod
    def choices(cls):
        """
        Utility function to generate a tuple of choices through enums.
        """
        return ((key.value, key.name) for key in cls)


class Duration(BotEnum):
    """
    Duration Enum.
    """
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"


class Level(BotEnum):
    """
    Level Enum.
    """
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class Action(BotEnum):
    """
    Action Enum.
    """
    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"


class Button(BotEnum):
    """
    Button Enum.
    """
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class Shortcut(BotEnum):
    """
    Shortcut Enum.
    """
    SHIFT = "shift"
    CTRL = "ctrl"
    ALT = "alt"


class State(BotEnum):
    """
    State Enum.
    """
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class SkillLevel(BotEnum):
    """
    SkillLevel Enum.
    """
    MAX = "max"
    DISABLE = "disable"
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE = 12
    THIRTEEN = 13
    FOURTEEN = 14
    FIFTEEN = 15
    SIXTEEN = 16
    SEVENTEEN = 17
    EIGHTEEN = 18
    NINETEEN = 19
    TWENTY = 20
    TWENTY_ONE = 21
    TWENTY_TWO = 22
    TWENTY_THREE = 23
    TWENTY_FOUR = 24
    TWENTY_FIVE = 25
    TWENTY_SIX = 26
    TWENTY_SEVEN = 27
    TWENTY_EIGHT = 28
    TWENTY_NINE = 29
    THIRTY = 30


class Skill(BotEnum):
    """
    Skill Enum.
    """
    HEAVENLY_STRIKE = "heavenly_strike"
    DEADLY_STRIKE = "deadly_strike"
    HAND_OF_MIDAS = "hand_of_midas"
    FIRE_SWORD = "fire_sword"
    WAR_CRY = "war_cry"
    SHADOW_CLONE = "shadow_clone"


class Perk(BotEnum):
    """
    Perk Enum.
    """
    NO_PERK = "no_perk",
    MEGA_BOOST = "mega_boost"
    POWER_OF_SWIPING = "power_of_swiping"
    ADRENALINE_RUSH = "adrenaline_rush"
    MAKE_IT_RAIN = "make_it_rain"
    MANA_POTION = "mana_potion"
    DOOM = "doom"
    CLAN_CRATE = "clan_crate"


class Panel(BotEnum):
    """
    Panel Enum.
    """
    MASTER = "master"
    HEROES = "heroes"
    EQUIPMENT = "equipment"
    PETS = "pets"
    ARTIFACTS = "artifacts"
    SHOP = "shop"


class EquipmentTab(BotEnum):
    """
    EquipmentTab Enum.
    """
    SWORD = "sword"
    HEADGEAR = "headgear"
    CLOAK = "cloak"
    AURA = "aura"
    SLASH = "slash"


class Timeout(BotEnum):
    """
    Timeout Enum.
    """
    FUNCTION_TIMEOUT = 40
    BOSS_TIMEOUT = 10


class Minigame(BotEnum):
    """
    Minigame Enum.
    """
    COORDINATED_OFFENSIVE = "coordinated_offensive"
    ASTRAL_AWAKENING = "astral_awakening"
    HEART_OF_MIDAS = "heart_of_midas"
    FLASH_ZIP = "flash_zip"
    FORBIDDEN_CONTRACT = "forbidden_contract"


class HeroType(BotEnum):
    """
    HeroType Enum.
    """
    MELEE = "melee"
    SPELL = "spell"
    RANGED = "ranged"


class Color(BotEnum):
    """
    Color Enum.
    """
    WHITE = (255, 255, 255)
    COLLECT_GREEN = (101, 155, 28)
    SKILL_CANT_LEVEL = (73, 72, 73)
    DISCOVER = (60, 184, 174)
    ENCHANT = (235, 167, 12)
