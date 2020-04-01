from django.db.models import Q

from settings import (
    VERSION, TESSERACT_PATH, MAX_STAGE
)

from modules.auth.authenticator import Authenticator

from modules.bot.core.configurations import (
    GAME_IMAGES, GAME_LOCATIONS, GAME_REGIONS, ARTIFACTS, MAX_LEVEL_ARTIFACTS
)
from modules.bot.core.globals import Globals
from modules.bot.core.shortcuts import shortcuts_handler
from modules.bot.core.exceptions import ServerTerminationEncountered, TerminationEncountered
from modules.bot.core.attributes import DynamicAttributes
from modules.bot.core.properties import Properties
from modules.bot.core.decorators import wait_afterwards, BotProperty as bot_property
from modules.bot.core.utilities import bot_logger, format_delta, delta_from_value_string
from modules.bot.core.enumerations import (
    Button, SkillLevel, Skill, Perk, Panel, EquipmentTab,
    Timeout, Minigame, HeroType, Color
)

from modules.bot.external.imagesearch import imagesearcharea, click_image

from datetime import datetime, timedelta

from pytesseract import pytesseract

from imagehash import average_hash

from apscheduler.schedulers.base import STATE_RUNNING, STATE_STOPPED, STATE_PAUSED
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.background import BackgroundScheduler

from pyautogui import FailSafeException

from PIL import Image

from contextlib import contextmanager

import numpy as np
import threading
import random
import time
import sys
import cv2

# Create a module level reference to our globals utility wrapper.
# We can use this to check if certain pieces of functionality
# should be executed or not.
_globals = Globals()

# Ensure we're using the correct tesseract executable
# included within the distributable.
pytesseract.tesseract_cmd = TESSERACT_PATH


class Bot(object):
    """
    Core Bot Class.
    """
    def __init__(self, configuration, window, shortcuts, instance, run=True):
        """
        Initializing a new bot instance.
        """
        # Local level import of session and statistics.
        # Avoid circular imports.
        from db.models import Session, Statistics

        self._should_terminate = False
        self._should_pause = False
        self._last_stage = None
        self._last_snapshot = None
        self._advanced_start = None

        self.configuration = configuration
        self.window = window
        self.shortcuts = shortcuts
        self.instance = instance

        self.instance.configuration = self.configuration
        self.instance.window_json = self.window.dump()
        self.instance.shortcuts = self.shortcuts

        self.owned_artifacts = None
        self.next_artifact_upgrade = None

        self.prestige_master_levelled = False
        self.prestige_skills_levels = {skill.value: 0 for skill in Skill}

        self.logger = bot_logger(instance=self.instance, configuration=self.configuration)

        self.images = DynamicAttributes(attributes=GAME_IMAGES, logger=self.logger)
        self.locations = DynamicAttributes(attributes=GAME_LOCATIONS, logger=self.logger)
        self.regions = DynamicAttributes(attributes=GAME_REGIONS, logger=self.logger)

        self.properties = Properties(instance=self.instance, logger=self.logger)

        self.session = Session.objects.generate(instance=self.instance, configuration=self.configuration, logger=self.logger)
        self.statistics = Statistics.objects.grab(instance=self.instance)

        self.statistics.session_statistics.sessions.add(self.session)

        self.scheduler = self._setup_function_scheduler()
        self.enabled_skills = self._calculate_enabled_skills()
        self.minigame_order = self._calculate_minigame_order()
        self.enabled_perks = self._calculate_enabled_perks()

        # Perform an initial datetime calculation for all of our
        # calculation based properties once on initialization.
        self._calculate_all()
        # Build out instances initialization information.
        # Make sure we log some information about the bot being started.
        self._initialized()

        # Running automatically after initialization is finished.
        # Usually do not need to not run after initialization.
        if run:
            self.run()

    def _initialized(self):
        """
        Perform some final setup of the core bot instance.
        """
        self.instance.start(session=self.session)

        # Log some generic information about this bot session and some of
        # the values that are associated with this instance.
        self.logger.info("========================================================================")
        self.logger.info("Titandash Bot (v{version}) Initialized...".format(version=VERSION))
        self.logger.info("{session}".format(session=self.session.__repr__()))
        self.logger.info("{window}".format(window=self.window.__repr__()))
        self.logger.info("{configuration}".format(configuration=self.configuration.__repr__()))
        self.logger.info("========================================================================")

        # Setting the authenticator backend to an online state for the user
        # currently available and logged in to the system.
        Authenticator.online(instance=self.instance)

    def _setup_function_scheduler(self):
        """
        Setup the background function scheduler present on a bot instance, any interval based jobs are added here.
        """
        _scheduler = BackgroundScheduler()

        # Find all interval based bot properties.
        # These should be populated at run time and available
        # when instances are initialized.
        for prop in bot_property.intervals():
            _scheduler.add_job(func=getattr(self, prop["name"]), trigger=IntervalTrigger(seconds=prop["interval"]), id=prop["name"])
            # Log some information about the scheduled function that's been added to the scheduler.
            self.logger.debug("function: {function} has been scheduled. (every {interval} second(s)).".format(function=prop["name"], interval=prop["interval"]))

        return _scheduler

    def _snapshot(self, region=None, downsize=None):
        """
        Attempt to take a screenshot of the current in game screen.
        """
        self._last_snapshot = self.window.screenshot(region=region)

        # Downsize the image slightly if we've specified that it should be
        # made smaller by a certain scale.
        if downsize:
            self._last_snapshot.thumbnail((
                self._last_snapshot.width * downsize,
                self._last_snapshot.height * downsize
            ))

        # Make sure we return the snapshot we just took
        # of the current window.
        return self._last_snapshot

    def _search(self, image, region=None, precision=0.8, position=False, im=None, image_name=None):
        """
        Attempt to search for the specified image(s) within the in game screen or region.
        """
        # Generate a dictionary of search kwargs that can be used
        # with our external image searching library.
        _search = {
            "x1": region[0] if region else self.window.x,
            "y1": region[1] if region else self.window.y,
            "x2": region[2] if region else self.window.width,
            "y2": region[3] if region else self.window.height,
            "precision": precision,
            "im": im if region else self._snapshot() if not im else im,
            "logger": self.logger
        }

        # Default our position value to the no image could be found
        # default value [-1, -1].
        _position = [-1, -1]

        # If a list of images is being searched for, begin looping through
        # all images specified, once the first image is found, the loop is broken.
        if isinstance(image, list):
            for _image in image:
                # Attempt to perform imagesearcharea on the derived search kwargs.
                _position = imagesearcharea(window=self.window, image=_image, **_search)
                # Has the image been found on the screen or region?
                if _position[0] != -1:
                    break

        # Otherwise, we'll use the base imagesearcharea functionality on the image
        # specified to be searched for.
        else:
            _position = imagesearcharea(window=self.window, image=image, **_search)

        if _position[0] != -1:
            # The image was successfully found on the screen. Log some information about the
            # successful image search.
            self.logger.debug("successfully found image: {image}.".format(image=image_name or image))
        else:
            # The image could not be found on the screen at all, log some information
            # about the un-successful image search.
            self.logger.debug("could not find image: {image}.".format(image=image_name or image))

        # Do we want to return both whether or not the image was found,
        # and the position that the image was found at?
        if position:
            return _position[0] != -1, _position

        # Otherwise, we can just return whether or not the image was found.
        return _position[0] != -1

    def _is_color(self, point, color=None, color_range=None):
        """
        Given a point, determine if that point is currently a specific color or color range.
        """
        if color and color_range:
            # Shouldn't be able to specify both of these
            # parameters, unable to know which one to look for.
            raise ValueError("only one of 'color' or 'color_range' should be present, but not both.")

        # Take a snapshot of the current in game screen.
        self._snapshot()
        # Get the color of the point for the current
        # last screenshot available.
        _point = self._last_snapshot.getpixel(xy=point)

        # No padding or point modifications is needed for the color check.
        # Since we're using the snapshot functionality which will take the
        # size and location of the window into account.
        if color:
            return _point == color
        # A range of colors have been specified, we can use this to account for
        # some irregularity in the colors present in certain locations.
        if color_range:
            return color_range[0][0] <= _point[0] <= color_range[0][1] and \
                   color_range[1][0] <= _point[1] <= color_range[1][1] and \
                   color_range[2][0] <= _point[2] <= color_range[2][1]

    def _process(self, scale=1, threshold=None, region=None, use_current=True):
        """
        Attempt to perform an optical character recognition call on a provided window region, or on the entire screen.
        """
        _image = self._snapshot(region=region) if use_current else self._last_snapshot
        _image = np.array(_image)

        # Scale and desaturate image.
        _image = cv2.resize(_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        _image = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)

        # Perform threshold on the image if it's enabled.
        # Threshold will ensure that certain colored pieces are removed.
        if threshold:
            retr, _image = cv2.threshold(_image, 230, 255, cv2.THRESH_BINARY)
            contours, hier = cv2.findContours(_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Drawing black over any contours smaller than our specified threshold.
            # Removing un-wanted blobs from the image grabbed.
            for contour in contours:
                if cv2.contourArea(contour) < threshold:
                    cv2.drawContours(_image, [contour], 0, (0,), -1)

        # Re-create the image from our numpy array through the Pillow Image module.
        # Threshold or not, an Image is always returned.
        return Image.fromarray(_image)

    def _parse_advanced_start(self, stage):
        """
        Attempt to parse out the advanced start stage value.
        """
        try:
            # Can the stage parsed be coerced into a proper integer.
            # This determines if most of the parsing will take place.
            self._advanced_start = int(stage)
        except (ValueError, TypeError):
            self._advanced_start = None

        if self._advanced_start:
            if self._advanced_start > MAX_STAGE:
                # The advanced start we parsed out is larger than the actual
                # current in game stage cap, safe to say a malformed string
                # was grabbed, let's just fallback to none value.
                self.logger.warn("advanced start: {stage} is greater than the stage cap: {max_stage}, defaulting to none.".format(
                    stage=stage, max_stage=MAX_STAGE)
                )
                # Set advanced start to a zero value.
                # At least allows us to skip functionality if needed.
                self._advanced_start = None
        else:
            # Log some information about the fact that the advanced
            # start value is non truthy (probably none type).
            self.logger.warn("invalid advanced start value was parsed: {value}.".format(value=self._advanced_start))

    def _calculate_minigame_order(self):
        """
        Calculate and parse the order that mini-games will be executed.
        """
        _minigames = []

        # Each minigame will use its own key, based on the configuration boolean
        # present to enable or disable each one.
        for minigame, enabled in [
            [Minigame.COORDINATED_OFFENSIVE.value, self.configuration.enable_coordinated_offensive],
            [Minigame.ASTRAL_AWAKENING.value, self.configuration.enable_astral_awakening],
            [Minigame.HEART_OF_MIDAS.value, self.configuration.enable_heart_of_midas],
            [Minigame.FLASH_ZIP.value, self.configuration.enable_flash_zip],
            [Minigame.FORBIDDEN_CONTRACT.value, self.configuration.enable_forbidden_contract]
        ]:
            if enabled:
                _minigames.append(minigame)

        # Log some debugging information about the enabled minigames.
        self.logger.debug("enabled minigames: {minigames}".format(minigames=", ".join(_minigames) if _minigames else "none"))

        return _minigames

    def _calculate_enabled_perks(self):
        """
        Calculate and parse the perks that will be set as enabled.
        """
        _perks = []

        for perk in Perk:
            # Skip enabled check if the perk in our for loop
            # if our "no perk" perk.
            if perk.value == Perk.NO_PERK.value:
                continue

            # Is the current perk enabled through the configuration?
            # Only perks set as enabled should be included.
            if getattr(self.configuration, "enable_{key}".format(key=perk.value)):
                _perks.append(perk.value)

        # Log some debugging information about the enabled minigames.
        self.logger.debug("enabled perks: {perks}".format(perks=", ".join(_perks) if _perks else "none"))

        return _perks

    def _calculate_enabled_skills(self):
        """
        Calculate and parse the skills that will be set as enabled.
        """
        _skills = []

        for skill in Skill:
            # Is the current skill enabled through the configuration?
            # Only skills set as enabled should be included.
            if getattr(self.configuration, "interval_{skill}".format(skill=skill.value)) != 0:
                _skills.append(skill.value)

        # Log some debugging information about the enabled minigames.
        self.logger.debug("enabled skills: {perks}".format(perks=", ".join(_skills) if _skills else "none"))

        return _skills

    def _calculate(self, attr, interval=None, dt=None, log=True):
        """
        Base calculate method to determine and update the next datetime that the specified property should be executed.
        """
        now = datetime.now()

        # Interval based calculations require an interval to
        # be specified in seconds only.
        if interval is not None:
            dt = now + timedelta(seconds=interval)

        # Essentially Props.attr = dt.
        setattr(self.properties, attr, dt)

        # Generate a log record about the calculated function if enabled.
        # Otherwise the logging is skipped, may prove useful for certain properties.
        if log:
            self.logger.info("{attr} will be executed in {time}".format(attr=attr, time=format_delta(dt - now)))

    def _calculate_all(self):
        """
        Re-calculate all of the calculation based functions present on a bot instance.
        """
        for calculate in [f for f in dir(self) if f.startswith("calculate_")]:
            # Attempt to dynamically grab each calculation function and
            # run them manually, ensuring that properties are all updated.
            getattr(self, calculate)()

    def click(self, point, clicks=1, interval=0.0, button=Button.LEFT, offset=5, pause=0.0):
        """
        Perform a click with the specified options against the current window.
        """
        self.window.click(point=point, clicks=clicks, interval=interval, button=button, offset=offset, pause=pause)

    def drag(self, start, end, button=Button.LEFT, pause=0.5):
        """
        Perform a drag with the specified options against the current window.
        """
        self.window.drag(start=start, end=end, button=button, pause=pause)

    def click_image(self, image, position, button=Button.LEFT, offset=5, pause=0.0):
        """
        Perform a click on the specified image against the current window.
        """
        click_image(window=self.window, image=image, position=position, button=button, offset=offset, pause=pause)

    def find_and_click(self, image, region=None, precision=0.8, button=Button.LEFT, offset=5, pause=0.0, padding=None, log=None):
        """
        Attempt to find and click on the specified image against the current window.
        """
        _found, _position = self._search(image=image, region=region, precision=precision, position=True)

        # Is the image specified (or images) currently
        # present on the window or within the region.
        if _found:
            if log:
                # Logging is enabled, output the specified message
                # that's set to be logged when image is found.
                self.logger.info(log)

            if padding:
                # Padding is enabled, modify our point properly
                # so the location is correct.
                _position = (
                    _position[0] + padding[0],
                    _position[1] + padding[1]
                )

                # Perform a normal click on the point
                # we've parsed out with the proper padding.
                self.click(point=_position, button=button, offset=offset, pause=pause)

            # Otherwise, padding isn't present at all.
            # Just use default click image function.
            else:
                self.click_image(image=image, position=_position, button=button, offset=offset, pause=pause)

        # Return a boolean representing whether or not our image
        # (or images) were found at all and clicked on.
        return _found

    @bot_property(queueable=True, tooltip="Calculate the next time that in game skills will be executed.")
    def calculate_next_skill_execution(self, skill=None):
        """
        Calculate the next datetime(s) that each skill in game will be executed.
        """
        calculate = [s.value for s in Skill] if not skill else [skill]

        interval_key = "interval_{skill}"
        next_key = "next_{skill}"

        # Loop through the skill specified, or all skills available and attempt to
        # update each one next calculation time.
        for skill in calculate:
            interval = getattr(self.configuration, interval_key.format(skill=skill))
            if interval != 0:
                self._calculate(attr=next_key.format(skill=skill), interval=interval)

    @bot_property(queueable=True, tooltip="Calculate the next time that the prestige process will take place.")
    def calculate_next_prestige(self):
        """
        Calculate when the next timed prestige will take place.
        """
        self._calculate(attr="next_prestige", interval=self.configuration.prestige_x_minutes * 60)

    @bot_property(queueable=True, tooltip="Calculate the next time that the perk activation process will take place.")
    def calculate_next_perk_check(self):
        """
        Calculate when the next timed perk check will take place.
        """
        # Prevent next timed check if perks are only enabled when tournaments
        # are initially entered.
        if self.configuration.enable_perk_usage and self.configuration.enable_perk_only_tournament:
            return

        self._calculate(attr="next_perk_check", interval=self.configuration.use_perks_every_x_hours * 60 * 60)

    @bot_property(queueable=True, tooltip="Calculate the next time that the sword master levelling process will take place.")
    def calculate_next_master_level(self):
        """
        Calculate when the next sword master levelling process will take place.
        """
        self._calculate(attr="next_master_level", interval=self.configuration.master_level_every_x_seconds)

    @bot_property(queueable=True, tooltip="Calculate the next time that the heroes levelling process will take place.")
    def calculate_next_heroes_level(self):
        """
        Calculate when the next heroes levelling process will take place.
        """
        self._calculate(attr="next_heroes_level", interval=self.configuration.hero_level_every_x_seconds)

    @bot_property(queueable=True, tooltip="Calculate the next time that the headgear swap process will take place.")
    def calculate_next_headgear_swap(self):
        """
        Calculate when the next headgear swap process will take place.
        """
        self._calculate(attr="next_headgear_swap", interval=self.configuration.headgear_swap_every_x_seconds)

    @bot_property(queueable=True, tooltip="Calculate the next time that the skills levelling process will take place.")
    def calculate_next_skills_level(self):
        """
        Calculate when the next skills levelling process will take place.
        """
        self._calculate(attr="next_skills_level", interval=self.configuration.level_skills_every_x_seconds)

    @bot_property(queueable=True, tooltip="Calculate the next time that the skills activation process will take place.")
    def calculate_next_skills_activation(self):
        """
        Calculate when the next skills activation process will take place.
        """
        self._calculate(attr="next_skills_activation", interval=self.configuration.activate_skills_every_x_seconds)

    @bot_property(queueable=True, tooltip="Calculate the next time that the statistics update process will take place.")
    def calculate_next_statistics_update(self):
        """
        Calculate when the next statistics update process will take place.
        """
        self._calculate(attr="next_statistics_update", interval=self.configuration.update_statistics_every_x_minutes * 60)

    @bot_property(queueable=True, tooltip="Calculate the next time that the miscellaneous actions process will take place.")
    def calculate_next_miscellaneous_actions(self):
        """
        Calculate when the next miscellaneous functions process will take place.
        """
        self._calculate(attr="next_miscellaneous_actions", interval=self.configuration.miscellaneous_actions_every_x_seconds)

    @bot_property(queueable=True, tooltip="Calculate the next time that the daily achievement check process will take place.")
    def calculate_next_daily_achievement_check(self):
        """
        Calculate when the next daily achievement check process will take place.
        """
        self._calculate(attr="next_daily_achievement_check", interval=self.configuration.daily_achievements_check_every_x_hours * 60 * 60)

    @bot_property(queueable=True, tooltip="Calculate the next time that the milestone check process will take place.")
    def calculate_next_milestone_check(self):
        """
        Calculate when the next milestone check process should take place.
        """
        self._calculate(attr="next_milestone_check", interval=self.configuration.milestones_check_every_x_hours * 60 * 60)

    @bot_property(queueable=True, tooltip="Calculate the next time that the raid notifications check process will take place.")
    def calculate_next_raid_notifications_check(self):
        """
        Calculate when the next raid notifications process will take place.
        """
        self._calculate(attr="next_raid_notifications_check", interval=self.configuration.raid_notifications_check_every_x_minutes * 60)

    @bot_property(queueable=True, tooltip="Calculate the next time that the break process will take place.")
    def calculate_next_break(self):
        """
        Calculate when the next break process will take place.
        """
        if self.configuration.enable_breaks:
            now = datetime.now()

            # Calculating when the next break will begin.
            jitter = random.randint(-self.configuration.breaks_jitter, self.configuration.breaks_jitter)
            jitter = self.configuration.breaks_minutes_required + jitter

            next_break_dt = now + timedelta(minutes=jitter)

            # Calculate the datetime to determine when the bot will be resumed after a break takes place.
            resume_jitter = random.randint(self.configuration.breaks_minutes_min, self.configuration.breaks_minutes_max)
            next_break_res = next_break_dt + timedelta(minutes=resume_jitter + 10)

            self._calculate(attr="next_break", dt=next_break_dt, log=False)
            self._calculate(attr="break_resume", dt=next_break_res, log=False)

            # Using a custom log message to ensure proper, readable information is outputted
            # about the current breaks process datetimes.
            self.logger.info("the next in game break will take place in {time_1} and resume in {time_2}".format(
                time_1=format_delta(next_break_dt - now),
                time_2=format_delta(next_break_res - now)
            ))

    @bot_property(queueable=True, tooltip="Calculate the next time that the fairy tapping process will take place.")
    def calculate_next_fairy_tap(self):
        """
        Calculate when the next fairy tapping process will take place.
        """
        self._calculate(attr="next_fairy_tap", interval=self.configuration.fairy_tap_every_x_seconds)

    @bot_property(queueable=True, tooltip="Calculate the next time that the minigame tapping process will take place.")
    def calculate_next_minigames_tap(self):
        """
        Calculate when the next minigame tapping process will take place.
        """
        if self.configuration.enable_minigames:
            self._calculate(attr="next_minigames_tap", interval=self.configuration.minigames_every_x_seconds)

    @bot_property(interval=5, wrap_name=False)
    def parse_current_stage(self):
        """
        Attempting to update the current stage in game.
        """
        _result = pytesseract.image_to_string(
            image=self._process(scale=5, threshold=150, region=self.regions.stage_ocr, use_current=True),
            config="--psm 7 nobatch digits"
        )

        # Ensure we strip out any non digit characters from the result if any are present.
        # Stages can only contain integers.
        _result = ''.join(filter(lambda x: x.isdigit(), _result))
        # Can we now successfully get an integer from the result?
        # If we have an integer, we can properly check conditionals.
        if _result:
            try:
                _result = int(_result)
            except ValueError:
                # No stage could be parsed out at all, exit early without
                # setting any properties or updating any instance values.
                return

            # Stage is available, check conditionals then update bot values.
            if _result > MAX_STAGE or self.properties.advanced_start and _result < self.properties.advanced_start:
                # Stage parsed is obviously malformed (> max stage in game), or, the stage parsed is <
                # then the current available advanced stage variable, this is updated with each prestige
                # and acts as a good barrier for incorrect stage parsed that still returned integers.
                return

            self._last_stage = self.properties.stage
            self.properties.stage = _result

    @bot_property(queueable=True, tooltip="Parse out the current levels of skills currently in game.", transition=True)
    def parse_current_skills(self, skill=None):
        """
        Attempting to parse out the level of each skill in game.
        """
        self.logger.info("attempting to parse out all current skill levels in game.")

        with self.goto_master(collapsed=False):
            # Loop through all available in game skills, or loop once over the
            # specified skill, attempting to parse out the skills level.
            for _skill in [s.value for s in Skill] if not skill else [skill]:
                _region = self.regions.skill_level_regions[_skill]
                _result = pytesseract.image_to_string(
                    image=self._process(scale=3, region=_region, use_current=True),
                    config="--psm 7"
                )

                # Checking for a potential inclusion of the "," or "." character.
                # Since skill parsing tries to grab a string like "Lv. 30", the dot
                # can be used to split text and get level number.
                for _check in [",", "."]:
                    if _check in _result:
                        # Split on character found and grab the last index from result.
                        _result = _result.split(_check)[-1]

                # Ensure we remove any whitespace on either side of the result string.
                _result = _result.strip()

                # Attempt to coerce our result text for this skill
                # into a proper integer.
                try:
                    _result = int(_result)
                except ValueError:
                    self.prestige_skills_levels[_skill] = 0
                    self.logger.warn("skill: {skill} was parsed incorrectly, defaulting to level 0 instead...".format(skill=_skill))
                    continue

                # Update the current skill level for current skill in loop.
                # These values are reset on each prestige and parsed each subsequent prestige.
                self.prestige_skills_levels[_skill] = _result
                self.logger.info("skill: {skill} was parsed as level: {level}".format(skill=_skill, level=_result))

    @bot_property(queueable=True, tooltip="Parse out the list of artifacts that are available for upgrading.")
    def get_upgrade_artifacts(self):
        """
        Parse and build out a list of all discovered and owned artifacts in game that will be upgraded during each prestige.
        """
        _lst = []

        if not self.configuration.enable_artifact_upgrade:
            # Artifact upgrades are disabled outright, we can skip the parsing process
            # and just use the empty list instead.
            self.owned_artifacts = _lst
            self.logger.info("artifact purchase is disabled, no artifacts will be upgraded.")

        # Grabbing configuration values that represent whether or not specific artifacts or
        # tiers of artifacts will be upgraded or ignored when a prestige takes place.
        tiers = self.configuration.upgrade_owned_tier.all().values_list("tier", flat=True)
        ignore = self.configuration.ignore_artifacts.all().values_list("name", flat=True)
        upgrade = self.configuration.upgrade_artifacts.all().values_list("name", flat=True)

        # Are there any artifacts owned currently for the instance that's currently having
        # upgrade artifacts parsed out?
        artifacts = self.statistics.artifact_statistics.owned()

        # If no artifacts are actually owned right now for this bot instance, we can attempt
        # to parse artifacts and grab them again.
        if artifacts.count() == 0:
            self.logger.info("no owned artifacts available, attempting to parse owned artifacts from game...")
            # Parse artifacts and try to grab them again.
            self.parse_artifacts()
            # Grab owned artifacts again after parsing
            # has taken place.
            artifacts = self.statistics.artifact_statistics.owned()

        # If no artifacts are available at all to upgrade, let's default
        # to disabling the functionality completely.
        # Owned artifacts still aren't present after we've attempted
        # to parse artifacts from the game, disable this functionality for the session.
        if artifacts.count() == 0:
            self.logger.warn("no artifacts were found after parsing, disabling artifact purchase for this session.")
            # Disable and set list to an empty list.
            self.configuration.enable_artifact_upgrade = False
            self.owned_artifacts = _lst
        else:
            # Generate the list with the actual artifacts that will be upgraded
            # in game when a prestige takes place. Making sure we exclude max level artifacts
            # and filter on artifacts in the tier specified, or specific artifacts chosen.
            _lst = list(artifacts.exclude(
                artifact__name__in=MAX_LEVEL_ARTIFACTS + list(ignore)
            ).filter(
                Q(artifact__tier__tier__in=tiers) |
                Q(artifact__name__in=upgrade)
            ).values_list("artifact__name", flat=True))

            if _lst:
                # Should we shuffle the list to add some randomness to the list
                # of artifacts that will be upgraded.
                if self.configuration.shuffle_artifacts:
                    random.shuffle(_lst)

            # Setting owned artifacts on current instance. Regardless of artifacts present or not,
            # if we make it here, we can safely set this to populated list, or empty list.
            self.logger.debug("artifacts: {artifacts} available for upgrade throughout this session.".format(artifacts=", ".join(_lst)))
            self.owned_artifacts = _lst

    @bot_property(queueable=True, tooltip="Update the next artifact that will be purchased when the next prestige takes place.")
    def update_next_artifact_purchase(self):
        """
        Update and retrieve the next artifact purchase based on the current set of owned artifacts.
        """
        if not self.owned_artifacts:
            # No artifacts are available, let's just set our property to a none value.
            # No artifact should be purchased on prestige.
            self.properties.next_artifact_upgrade = None

        # We can loop through available artifacts and make sure we iterate through each one
        # starting from the beginning once we've reached the end.
        try:
            _next = self.owned_artifacts[self.owned_artifacts.index(self.next_artifact_upgrade) + 1]
        except (ValueError, IndexError):
            # A value error will occur when the next index does not exist in the list of owned
            # artifacts, or when the index found is outside of the available length of the list.
            _next = self.owned_artifacts[0]

        self.properties.next_artifact_upgrade = _next
        self.logger.info("next artifact purchase: {artifact}.".format(artifact=_next))

    @bot_property(queueable=True, tooltip="Parse out the newest hero present in game that contains a non zero dps value.", transition=True)
    def parse_newest_hero(self):
        """
        Attempting to parse out and retrieve information about the newest hero present and whether or not the damage type has changed.
        """
        if self.configuration.enable_headgear_swap:
            with self.goto_heroes(collapsed=False):
                # Generate a default value for the newest hero
                # parsed, if one is found, set it here.
                _new = None

                for hero_locations in self.regions.hero_parse:
                    # Looping through each configured hero location, these really represent
                    # different locations (starting from the top of the hero panel) where each
                    # hero and their data should be located.
                    hero, dps = None, False

                    for location, region in hero_locations.items():
                        # "type" location for a hero means we can search for any of the three
                        # damage types available for each hero.
                        if location == "type":
                            if self._search(image=self.images.hero_melee_type, region=region):
                                hero = HeroType.MELEE
                            elif self._search(image=self.images.hero_spell_type, region=region):
                                hero = HeroType.SPELL
                            elif self._search(image=self.images.hero_ranged_type, region=region):
                                hero = HeroType.RANGED

                        # Check after type check for the dps of the current hero being parsed.
                        # If a hero does not contain the zero dps image, it means this hero has been levelled.
                        elif location == "dps":
                            dps = not self._search(image=self.images.hero_zero_dps, region=region)

                    if dps and hero:
                        _new = hero

                # If a new hero is successfully parsed out of the game, we can update our
                # properties and log some information about this.
                if _new:
                    self.properties.newest_hero = _new
                    self.logger.info("{typ} hero has been parsed out as newest hero with levels in game.".format(typ=_new))

    @bot_property(forceable=True, calculate="calculate_next_heroes_level", shortcut="shift+h", tooltip="Force hero levelling process in game.", transition=True)
    def level_heroes(self, force=False):
        """
        Execute all processes related to hero levelling in game.
        """
        if self.configuration.enable_heroes:
            if force or datetime.now() > self.properties.next_heroes_level:
                self.logger.info("{begin_or_force} heroes levelling process in game now.".format(
                    begin_or_force="running" if not force else "forcing"))

                with self.goto_heroes(collapsed=False):
                    # Generate the list of points in a reverse manor.
                    # [::-1] - Reverse the set of tuples.
                    # [1:]   - Skip the first index present in reversed list.
                    _locations = self.locations.hero_level_heroes[::-1][1:]

                    # Perform quick check to see if only the top of the heroes panel need to be levelled.
                    # We can skip "pagination" of hero levelling if this is the case to save time.
                    if self._search(image=self.images.hero_max_level):
                        self.logger.info("a max levelled hero was found, only the first set of heroes will be levelled.")
                        for point in _locations:
                            self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                        # Perform an early exist as well.
                        self.calculate_next_heroes_level()
                        self.parse_newest_hero()
                        return True

                    # Begin by levelling the set of heroes available in the list.
                    # Performing max level check after first set is levelled.
                    self.logger.info("levelling the first set of heroes available.")
                    for point in _locations:
                        self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                    # Travel to the bottom of the panel,
                    # or until a max level hero is found.
                    for i in range(6):
                        self.drag(start=self.locations.game_scroll_start, end=self.locations.game_scroll_bottom_end)

                        # Max level hero present after drag yet?
                        if self._search(image=self.images.hero_max_level):
                            self.logger.info("a max levelled hero was found, levelling all heroes now.")
                            break

                    # Begin level and scrolling process. Assumption is made here that all heroes
                    # are unlocked, meaning that some unneeded scrolls could take place.
                    self.logger.info("scrolling and levelling heroes on screen.")
                    # Looping until top of heroes panel (masteries) image is found.
                    while not self._search(image=self.images.hero_masteries):
                        self.logger.info("levelling heroes on screen...")
                        for point in self.locations.hero_level_heroes:
                            self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                        self.logger.info("dragging hero panel to the next set of heroes...")
                        self.drag(start=self.locations.hero_drag_start, end=self.locations.hero_drag_end)

                    # We always perform one additional levelling loop once we've reached the end
                    # of the process, just to make sure we don't miss any.
                    for point in self.locations.hero_level_heroes:
                        self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                # Once everything is done here, perform a quick hero parse so we
                # know which hero type is the newest.
                self.parse_newest_hero()

    @bot_property(forceable=True, calculate="calculate_next_master_level", shortcut="shift+m", tooltip="Force sword master levelling process in game.", transition=True)
    def level_master(self, force=False):
        """
        Execute all processes related to sword master levelling in game.
        """
        if self.configuration.enable_master:
            if force or datetime.now() > self.properties.next_master_level:
                self.logger.info("{begin_or_force} sword master levelling process in game now.".format(
                    begin_or_force="running" if not force else "forcing"))

                # Use the "level" flag to derive whether or not levelling will actually take
                # place at the time of execution. Should either take place once per prestige,
                # or once every x amount of seconds.
                _level = True
                # Levelling the sword master once when a prestige happens.
                if self.configuration.master_level_only_once:
                    if self.prestige_master_levelled:
                        _level = False
                    else:
                        self.logger.info("levelling the sword master once until the next prestige takes place.")
                        self.prestige_master_levelled = True

                # Levelling the sword master every x seconds.
                else:
                    self.logger.info("levelling sword master in game {clicks} time(s)".format(clicks=self.configuration.master_level_intensity))

                # Actual levelling process will not actually take place unless
                # the level flag has been set.
                if _level:
                    with self.goto_master(collapsed=False):
                        # Level the sword master the specified amount of clicks based
                        # on the configuration chosen by the user.
                        self.click(self.locations.master_level, clicks=self.configuration.master_level_intensity)

    @bot_property(forceable=True, calculate="calculate_next_skills_level", shortcut="shift+s", tooltip="Level enabled skills in game.", transition=True)
    def level_skills(self, force=False):
        """
        Level enabled skills in game.
        """
        def capped():
            """
            Retrieve two dictionary that represent capped and uncapped skills.
            """
            _capped, _uncapped = {}, {}

            for _skill in Skill:
                _chosen = getattr(self.configuration, "level_{skill}_cap".format(skill=_skill.value))

                # What has the user chosen to do with this skill?
                # Disabled or using a max level.
                if _chosen == SkillLevel.DISABLE.value:
                    continue
                if _chosen == SkillLevel.MAX.value:
                    _chosen = SkillLevel.THIRTY.value

                _current = self.prestige_skills_levels[_skill.value]
                _values = {
                    "current": _current,
                    "chosen": _chosen
                }

                # Is the user defined cap currently already reached? We have no need to try
                # and level a skill that's already the max level.
                if _chosen == _current or _current > _chosen:
                    _capped[_skill.value] = _values
                else:
                    _uncapped[_skill.value] = {**_values, **{"remaining": _chosen - _current}}

            # Return the list of capped and uncapped skills that are currently
            # present in the game.
            return _capped, _uncapped

        def level(key, maxout=False, clicks=1):
            """
            Perform actual levelling process of the specified skill.
            """
            _point = getattr(self.locations, "master_skill_{skill}".format(skill=key))
            _color = getattr(self.locations, "master_max_{skill}".format(skill=key))

            # Clicking on the derived point to begin the levelling process for the skill.
            self.logger.info("levelling skill: {skill} {clicks} time(s) now...".format(skill=key, clicks=clicks))
            self.click(point=_point, clicks=clicks, interval=0.3, pause=1)

            # Should the skill in question be levelled to it's maximum amount available?
            # We do this one second after the initial level so we can ensure the max level option is showing.
            if maxout:
                if self._is_color(point=_color, color=Color.WHITE):
                    self.click(point=_color, pause=0.5)

        def can_level(key):
            """
            Check to see if a skill can currently be levelled or not.
            """
            return not self._is_color(point=getattr(self.locations, "master_can_level_{skill}".format(skill=key)), color=Color.SKILL_CANT_LEVEL.value)

        def is_max(key):
            """
            Check to see if the skill is currently max level.
            """
            return self._search(image=self.images.master_skill_max_level, region=self.regions.skill_regions[key])

        def is_active(key):
            """
            Check to see if a skill is currently active or not.
            """
            return self._search(image=self.images.master_cancel_active_skill, region=self.regions.skill_regions[key])

        if self.configuration.enable_level_skills:
            if force or datetime.now() > self.properties.next_skills_level:
                self.logger.info("{begin_or_force} skill levelling process in game now.".format(
                    begin_or_force="running" if not force else "forcing"))

                # Retrieve values that represent skills that are currently capped, and skills that
                # are not yet capped or at max level.
                capped, uncapped = capped()
                # Are any uncapped skills available? If so, we can begin the process to level those
                # skills to their specified level cap.
                if uncapped:
                    # Goto the master panel in a non collapsed state so we can see all skills.
                    with self.goto_master(collapsed=False):
                        # Looping through all available uncapped skills.
                        for skill, values in uncapped.items():
                            if is_active(key=skill):
                                self.logger.info("skill: {skill} is already active, skipping levelling for now...".format(skill=skill))
                            elif not can_level(key=skill):
                                self.logger.info("skill: {skill} can not currently be levelled, skipping levelling for now...".format(skill=skill))

                            # Otherwise, we can check to see how much we need to level this skill by,
                            # whether or not we'll max it out or not.
                            else:
                                if values["chosen"] == SkillLevel.THIRTY:
                                    level(key=skill, maxout=True)
                                else:
                                    level(key=skill, clicks=values["remaining"])

                            # After levelling, let's check to see if the skill is now maxed
                            # through an image search, update parsed value if so.
                            if is_max(key=skill):
                                self.logger.info("skill: {skill} is max level, updating parsed skill level to max.".format(skill=skill))
                                self.prestige_skills_levels[skill] = SkillLevel.THIRTY.value
                            else:
                                # Otherwise, attempt to parse out the skill again
                                # through an ocr check.
                                self.parse_current_skills(skill=skill)

                self.calculate_next_skills_level()

    @bot_property(forceable=True, calculate="calculate_next_skills_activation", shortcut="ctrl+a", tooltip="Force all skills in game to be activated.", transition=True)
    def activate_skills(self, force=False):
        """
        Activate all enabled skills in game if they aren't already active.
        """
        if self.configuration.enable_activate_skills:
            if force or datetime.now() > self.properties.next_skills_activation:
                self.logger.info("{begin_or_force} skill activation process in game now.".format(
                    begin_or_force="running" if not force else "forcing"))

                # Skills activations takes place now, we need to determine or not any skills are enabled
                # and currently ready to be activated now.
                if self.enabled_skills:
                    # Ensure that any active panel is properly closed so that
                    # we can successfully see and click on all skills in game.
                    with self.no_panel():
                        # Looping through each available enabled skill, an additional check takes place
                        # to see if each enabled skill has surpassed it's configured threshold for activation.
                        for skill in self.enabled_skills:
                            if force or datetime.now() > getattr(self.properties, "next_{skill}".format(skill=skill)):
                                self.logger.info("{forcing_or_activating} skill: {skill} activation...".format(forcing_or_activating="forcing" if force else "running", skill=skill))
                                self.click(point=getattr(self.locations, "bar_{skill}".format(skill=skill)), clicks=3, pause=0.2)
                                self.calculate_next_skill_execution(skill=skill)

    @bot_property(transition=True)
    def use_perks(self, perks):
        """
        Attempt to activate or purchase the specified perk in game.
        """
        for perk in perks:
            self.logger.info("attempting to use perk: {perk} now.".format(perk=perk))
            # Traveling to the bottom of the expanded master panel for each individual
            # perk usage attempt, some perks may close the panel after usage.
            with self.goto_master(collapsed=False, top=False):
                # Grab the image associated with the current perk, we need to look
                # for it before attempting to use it.
                _image = getattr(self.images, "perk_{perk}".format(perk=perk))

                while not self._search(image=_image):
                    # Perk can not be found, just keep dragging until we find it.
                    self.drag(start=self.locations.scoll_start, end=self.locations.scroll_top_end)

                # This point reached means the perk is on the screen, let's get the position.
                _found, _position = self._search(image=_image, position=True)
                _point = (
                    _position[0] + self.locations.perk_push_x,
                    _position[1] + self.locations.perk_push_y
                )

                # Mega boost perk functions quite different;y then the other perks present
                # and available within the game.
                if perk == Perk.MEGA_BOOST:
                    # Is vip available to activate this perk?
                    if self._search(image=self.images.perk_vip_watch):
                        self.logger.info("using perk: {perk} with vip now...".format(perk=perk))
                        self.click(point=_point, pause=1)

                    # Otherwise, we can check to see if the user has enabled pi hole ads in their
                    # global settings.
                    else:
                        if _globals.pihole_enabled():
                            self.logger.info("attempting to use perk: {perk} through pi hole now...".format(perk=perk))
                            self.click(point=_point, pause=1)
                            # Check for perk header, looping until it's disappeared,
                            # which would represent the ad being finished.
                            while self._search(image=self.images.perk_perk_header):
                                self.click(point=self.locations.perk_okay, pause=2)
                                self.logger.info("waiting for pi hole to finish ad...")

                            # While loop exited, ad has been collected successfully.
                            self.logger.info("perk: {perk} has been used through pi hole successfully.".format(perk=perk))

                else:
                    # Attempting to open the purchase panel for this perk.
                    # If it's already active, no window will be opened, we can
                    # use this to determine whether or not to continue.
                    self.click(point=_point, pause=1)

                    # If the perk header isn't present after trying to open it,
                    # likely that the perk is already active, exit early.
                    if not self._search(image=self.images.perk_perks_header):
                        self.logger.info("unable to open perk: {perk} purchase panel, already active?".format(perk=perk))
                        return True

                    # Check for the diamond icon in the opened window in game,
                    # determine if we need to attempt a purchase or not.
                    if self._search(image=self.images.perk_diamond, region=self.regions.perk_purchase):
                        if self.configuration.enable_perk_diamond_purchase:
                            self.logger.info("purchasing perk: {perk} now.".format(perk=perk))
                            return self.click(point=self.locations.perks_okay, pause=1)
                        else:
                            self.logger.info("perk: {perk} requires diamonds to use, this is disabled currently, skipping...".format(perk=perk))
                            return self.click(point=self.locations.perks_cancel, pause=1)

                    # Otherwise, we can go ahead with the normal perk purchase flow.
                    self.logger.info("using perk: {perk} now.".format(perk=perk))
                    self.click(point=self.locations.perks_okay, pause=1)

    @bot_property(forceable=True, calculate="calculate_next_perk_check", shortcut="shift+c", tooltip="Force a perk check in game.", transition=True)
    def perks(self, force=False):
        """
        Execute the perk activation or purchase process in game.
        """
        if self.configuration.enable_perk_usage:
            # Are perks only enabled when a tournament is first joined? If so,
            # we should just leave early until the function is forced through tournaments checks.
            if self.configuration.enable_perk_only_tournament and not force:
                self.calculate_next_perk_check()
                return False

            if self.properties.next_perk_check:
                if force or datetime.now() > self.properties.next_perk_check:
                    self.logger.info("{begin_or_force} perks check in game now.".format(
                        begin_or_force="running" if not force else "forcing"))
                    # Travelling to the bottom of the master panel, expanded so we can view all perks in game.
                    with self.goto_master(collapsed=False, top=False):
                        self.use_perks(perks=self.enabled_perks)

    @bot_property(forceable=True, calculate="calculate_next_statistics_update", shortcut="shift+u", tooltip="Force a statistics update in game.", transition=True)
    def update_statistics(self, force=False):
        """
        Update the bot statistics by travelling to the statistics page in game and grabbing the values.
        """
        if self.configuration.enable_statistics:
            if force or datetime.now() > self.properties.next_statistics_update:
                self.logger.info("{begin_or_force} in game statistics update now.".format(
                    begin_or_force="running" if not force else "forcing"))
                # Leave boss fight in game if one is active so that stage transition does not take place
                # while the statistics update is taking place.
                with self.leave_boss():
                    # Sleep a little bit before attempting to goto the top of the heroes panel so
                    # that new hero levels do not cause the "top" of the panel to disappear after travelling.
                    time.sleep(2)

                    with self.goto_heroes():
                        # Make sure the top of the stats panel before attempting to travel
                        # to the bottom of the panel.
                        while not self._search(image=self.images.hero_statistics):
                            self.drag(start=self.locations.game_scroll_start, end=self.locations.game_scroll_top_end)
                        # Ensure that the stats panel has been opened before continuing.
                        while not self._search(image=self.images.statistic_title):
                            self.click(point=self.locations.hero_stats_collapsed, pause=1)

                        # Scroll to the bottom of the statistics panel.
                        time.sleep(1)
                        # Loop five times and travel down to the bottom of the statistics panel.
                        for i in range(5):
                            self.drag(start=self.locations.game_scroll_start, end=self.locations.game_scroll_bottom_end)

                        # Begin the recognition process to get values out of the images
                        # present in the statistics panel.
                        for key, region in self.regions.statistic_regions.items():
                            _result = pytesseract.image_to_string(
                                image=self._process(region=region),
                                config="--psm 7"
                            )

                            self.logger.debug("tesseract result ({key}): {result}".format(key=key, result=_result))

                            # First, we need to confirm that a number is present within our text result, if not numbers
                            # are present at all, its safe to assume that the ocr has failed.
                            if not any(c.isdigit() for c in _result):
                                self.logger.warn("no digits found in result, skipping key: {key}".format(key=key))
                                continue

                            # Otherwise, we can start trying to attempt to parse out the proper
                            # value from the result parsed out of the image.
                            try:
                                if len(_result.split(":")) == 2:
                                    _result = _result.split(":")[-1].replace(" ", "")
                                else:
                                    if key == "play_time":
                                        _result = " ".join(_result.split(" ")[-2:])
                                    else:
                                        _result = _result.split(" ")[-1].replace(" ", "")

                                # Finally. a small check to see that a value can be successfully made into an
                                # integer or float with either its last character taken off (K, M, %, etc).
                                # This check is not required for the "play_time' key.
                                if key != "play_time":
                                    try:
                                        if not _result[-1].isdigit():
                                            try:
                                                int(_result[:-1])
                                            except ValueError:
                                                try:
                                                    float(_result[:-1])
                                                except ValueError:
                                                    continue

                                        # Last character is a digit, value mau be a pure digit of some sort?
                                        else:
                                            try:
                                                int(_result)
                                            except ValueError:
                                                try:
                                                    float(_result)
                                                except ValueError:
                                                    continue

                                    except IndexError:
                                        self.logger.error("key: {key}, result: {result} could not be accessed properly.".format(key=key, result=_result))

                                self.logger.info("parsed result: {key} -> {result}".format(key=key, result=_result))

                                # Update the statistics instance attached to this bot session with the parsed
                                # result value. Save afterwards to update backend statistics model.
                                setattr(self.statistics.game_statistics, key, _result)
                                self.statistics.game_statistics.save()

                            # Gracefully continue our loop if a failure occurs.
                            # during the parsing process.
                            except ValueError:
                                self.logger.exception("could not parse key: {key}, result: {result}.".format(key=key, result=_result))

    @bot_property()
    def should_prestige(self):
        """
        Determine whether or not a prestige will take place.
        """
        # Check first for the randomized threshold prestige already waiting for execution.
        if self.configuration.enable_prestige_threshold_randomization and self.properties.next_randomized_prestige:
            # True  == randomized prestige is ready.
            # False == randomized prestige is setup but not ready yet.
            return datetime.now() > self.properties.next_randomized_prestige

        # Generate a ready flag, setting it to true once any of our configurable
        # thresholds are reached in game.
        _ready = False
        _now = datetime.now()

        if self.configuration.prestige_x_minutes:
            _ready = _now > self.properties.next_prestige

        # The timed threshold is one of the more important methods of
        # prestige checking, if it's not been reached, we can check secondary methods.
        if not _ready:
            # False out early if current stage is none for some reason.
            # We need a valid stage to perform these functions.
            if self.properties.stage is None:
                return False
            else:
                _current_stage = self.properties.stage

                # Prestige at an explicitly defined stage, once we surpass this stage, a prestige
                # should take place right away (barring randomization).
                if self.configuration.prestige_at_stage != 0 and _current_stage >= self.configuration.prestige_at_stage:
                    _ready = True
                # Prestige when the highest stage taken from the bot instances statistics
                # is surpassed.
                elif self.configuration.prestige_at_max_stage:
                    if _current_stage >= self.statistics.game_statistics.highest_stage:
                        _ready = True
                # Prestige at a defined percent of the current highest stage taken
                # from the bot instances statistics.
                elif self.configuration.prestige_at_max_stage_percent != 0:
                    _percent = float(self.configuration.prestige_at_max_stage_percent) / 100
                    _threshold = int(self.statistics.game_statistics.highest_stage * _percent)

                    # Is the current stage greater than or equal to the derived
                    # percent threshold to ensure a prestige takes place.
                    if _current_stage >= _threshold:
                        _ready = True

        # Ready has been hit proper, we now setup the randomized threshold values so that the next
        # time we check for prestige readiness, we use the random interval and check that enough
        # time has passed since it's been set.
        if _ready and self.configuration.enable_prestige_threshold_randomization:
            _jitter = random.randint(self.configuration.prestige_random_min_time, self.configuration.prestige_random_max_time)
            _datetime = _now + timedelta(minutes=_jitter)

            self.properties.next_randomized_prestige = _datetime

            # Return false explicitly after setting the next randomized prestige value.
            # The next time we enter this function, value is set so we check the
            # above conditional when entering instead.
            return False

        # Just return the base ready variable, this will happen when randomization is
        # disabled through the bots configuration.
        return _ready

    @bot_property()
    def create_prestige(self):
        """
        Create a new prestige instance and parse out the advanced start.

        Note that we are expecting the game to be on the prestige confirmation panel.
        """
        # Local level import of required models to avoid circular
        # import issues.
        from db.models import Artifact, Prestige

        # Begin by retrieving the time since a prestige last took place.
        # We must use the proper region based on whether or not an event is in progress.
        _region = self.regions.prestige_event["prestige_time_since"] if _globals.game_event_enabled() else self.regions.prestige_base["prestige_time_since"]
        _result = pytesseract.image_to_string(
            image=self._process(scale=3, region=_region, use_current=True),
            config="--psm 7"
        )

        self.logger.debug("tesseract result: {result}".format(result=_result))
        self.logger.info("attempting to parse hours:minutes:seconds from time since last prestige text.")

        try:
            hours, minutes, seconds = [int(t) for t in _result.split(":")]
        except ValueError:
            hours, minutes, seconds = None, None, None

        # Generate a delta from the values parsed from the time since last
        # prestige tesseract value.
        _delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        _artifact = None

        # Grab the actual artifact instance if one is going to be purchased
        # after this prestige is generated.
        if self.next_artifact_upgrade:
            _artifact = Artifact.objects.get(name=self.next_artifact_upgrade)

        _prestige = Prestige.objects.create(
            timestamp=datetime.now(),
            duration=_delta,
            stage=self.properties.stage,
            artifact=_artifact,
            session=self.session,
            instance=self.instance
        )

        self.logger.info("prestige instance generated: {prestige}".format(prestige=_prestige))

        self.statistics.prestige_statistics.prestiges.add(_prestige)
        self.statistics.prestige_statistics.save()

        # We also need to retrieve the advanced start value from the same screen.
        # Advanced start will allow us to improve stage parsing.
        _region = self.regions.prestige_event["prestige_advanced_start"] if _globals.game_event_enabled() else self.regions.prestige_base["prestige_advance_start"]
        _result = pytesseract.image_to_string(
            image=self._process(scale=5, threshold=100, region=_region, use_current=True),
            config="--psm 7 nobatch digits"
        )

        # Parse out the advanced start value, ensuring that any in-proper values
        # are filtered out (only digits allowed).
        _advanced_start = ''.join(filter(lambda x: x.isdigit(), _result))

        return _prestige, _advanced_start

    @bot_property(transition=True)
    def check_tournament(self):
        """
        Check that a tournament is available or active, joining if possible.
        """
        if self.configuration.enable_tournaments:
            # Making sure panels are all collapsed in case of expanded panel
            # when we enter this function (although that should not happen).
            with self.ensure_collapsed():
                # Looping to find a tournament here, there's a small change that the tournament is finished,
                # which will cause a star trail to circle the icon, Look until it's found.
                _found = False

                for i in range(5):
                    _found = self._search(image=self.images.no_panel_tournament)
                    # Have we found the image?
                    if _found:
                        break

                    # Sleep slightly in between each attempt to find the tournament icon.
                    time.sleep(0.2)

                if _found:
                    self.click(point=self.locations.tournament_icon, pause=2)
                    # The join image is present, before we do join the tournament, we must
                    # travel to the base prestige screen, create our prestige before joining.
                    if self._search(image=self.images.tournament_join):
                        self.click(point=self.locations.master_screen_top, pause=1)
                        # Travel to the master panel in game to get
                        # to the prestige button.
                        with self.goto_master():
                            self.click(point=self.locations.master_prestige, pause=3)

                            # Searching for the prestige confirmation button as well as the
                            # position of the button.
                            prestige_found, prestige_position = self._search(image=self.images.master_confirm_prestige, position=True)

                            if prestige_found:
                                # Parsing the advanced start value that is present before a prestige takes place.
                                # This is done to improve stage parsing to now allow values < advanced start.
                                # We also handle the prestige generation here.
                                prestige, advanced_start = self.create_prestige()

                                # Once we have all the information we need, we can go back to our tournament
                                # panel to join properly.
                                self.click(point=self.locations.master_screen_top, pause=1)

                                with self.ensure_collapsed():
                                    # Attempt to join the tournament proper after
                                    # collapsing any panels.
                                    self.click(point=self.locations.tournament_icon, pause=2)
                                    self.click(point=self.locations.tournament_join, pause=2)

                                    # Looking for the final prestige join confirmation, replicating
                                    # some of the base prestige functionality.
                                    self.find_and_click(image=self.images.master_confirm_prestige_final)

                                    return prestige, advanced_start

                    # Otherwise, maybe the tournament is over and we can collect a prize
                    # before leaving this function without any tournament join values found.
                    else:
                        self.find_and_click(image=self.images.tournament_collect, pause=2)
                        self.click(point=self.locations.game_middle, clicks=10, interval=0.5)

            # No tournament has been joined, and maybe a prize was collected, regardless, we
            # will return proper false flags.
            return False, None
        # Explicitly returning false flags if tournaments are disabled, since we still need
        # to prestige properly and this function needs to return.
        return False, None

    @bot_property(forceable=True, shortcut="shift+p", tooltip="Force a prestige in game to take place.", transition=True)
    def prestige(self, force=False):
        """
        Perform a prestige in game, joining tournaments or collecting rewards if they're available.
        """
        if self.configuration.enable_auto_prestige:
            if force or self.should_prestige():
                self.logger.info("{begin_or_force} prestige process in game now.".format(
                    begin_or_force="running" if not force else "forcing"))

                # Leave boss fight if one is available, and waiting slightly after to ensure that
                # current stage is up to date before trying to begin the prestige.
                with self.leave_boss():
                    with self.goto_master():
                        # Sleep slightly before even attempting to begin
                        # the prestige process.
                        time.sleep(5)

                        # Pause all scheduler functionality while prestige is taking place.
                        if self.scheduler.state == STATE_RUNNING:
                            self.scheduler.pause()

                        # Reset any properties that are reset or changed when a prestige takes place.
                        self.properties.newest_hero = None
                        self.prestige_skills_levels = {skill.value: 0 for skill in Skill}
                        self.prestige_master_levelled = False
                        # Reset the prestige randomization variable if randomization is currently enabled.
                        if self.configuration.enable_prestige_threshold_randomization:
                            if self.properties.next_randomized_prestige:
                                self.properties.next_randomized_prestige = None

                        # Perform tournament check. If tournaments are enabled, we can perform the normal prestige process
                        # and some extra functionality afterwards.
                        tournament_prestige, advanced_start = self.check_tournament()

                        if tournament_prestige:
                            # Tournament would have handled the prestige generation as well
                            # as the clicks to initialize the prestige process.
                            self.properties.last_prestige = tournament_prestige
                            self._parse_advanced_start(stage=advanced_start)
                            self.properties.stage = advanced_start or 0
                            # Sleep explicitly if a tournament was joined. Since we update the last
                            # prestige and advanced start right after that happens.
                            time.sleep(35)

                            # Should perks be ran since a prestige just took place?
                            if self.configuration.enable_perk_usage and self.configuration.enable_perk_only_tournament:
                                self.use_perks(perks=self.enabled_perks)

                            # Exit early as well.
                            return

                        # Otherwise, no tournament was available to join, but we can run through
                        # the normal prestige process to handle non tournament prestiges.
                        else:
                            # Clicking on the prestige button, and checking for the confirmation prompt.
                            self.click(point=self.locations.master_prestige, pause=3)

                            # Searching for the prestige confirmation button as well as the
                            # position of the button.
                            prestige_found, prestige_position = self._search(image=self.images.master_confirm_prestige, position=True)

                            if prestige_found:
                                # Parsing the advanced start value that is present before a prestige takes place.
                                # This is done to improve stage parsing to now allow values < advanced start.
                                # We also handle the prestige generation here.
                                prestige, advanced_start = self.create_prestige()

                                # Update our properties after generating the prestige values.
                                self.properties.last_prestige = prestige
                                self._parse_advanced_start(stage=advanced_start)
                                self.properties.stage = advanced_start or 0

                                self.click_image(image=self.images.master_confirm_prestige, position=prestige_position, pause=1)
                                prestige_final_found, prestige_final_position = self._search(image=self.images.master_confirm_prestige_final, position=True)
                                self.click_image(image=self.images.master_confirm_prestige_final, position=prestige_final_position, pause=35)

                        # Prestige has been finished at this point, begin executing al functionality
                        # that should occur after a prestige is done.
                        if self.scheduler.state == STATE_PAUSED:
                            self.scheduler.resume()
                        if self.configuration.prestige_x_minutes != 0:
                            self.calculate_next_prestige()

                        # Make sure we run through our base game actions once after a prestige.
                        self.level_master(force=True)
                        self.level_skills(force=True)
                        self.activate_skills(force=True)
                        # Add a small wait period after skills are activated,
                        # allowing us to gain some gold before levelling heroes.
                        time.sleep(2)
                        # Level up heroes in game, once we've waited to gain some gold.
                        self.level_heroes(force=True)

                        if self.configuration.enable_perk_usage and self.configuration.use_perk_on_prestige != Perk.NO_PERK:
                            self.use_perks(perks=[self.configuration.use_perk_on_prestige])

                        # Ensure artifacts are purchased and upgraded right after our prestige
                        # process and post functions have finished running.
                        self.artifacts()

    @bot_property(forceable=True, calculate="calculate_next_headgear_swap", tooltip="Force a headgear swap in game.", transition=True)
    def swap_headgear(self, force=False):
        """
        Attempt to swag the in game headgear to match the newest available heroes damage type.
        """
        if force or datetime.now() > self.properties.next_headgear_swap:
            self.logger.info("{begin_or_force} headgear swap process in game now.".format(
                begin_or_force="running" if not force else "forcing"))

            with self.goto_heroes(collapsed=False):
                # Ensure we manually run the hero parsing before even attempting
                # to swap headgear.
                self.parse_newest_hero()
                self.properties.function = self.swap_headgear.__name__

                _newest = self.properties.newest_hero

                # No newest hero could be found, calculate the next headgear swap and exit early.
                if not _newest:
                    self.calculate_next_headgear_swap()
                    return True

                # Travelling to the equipment panel at this point.
                # Then we can also open up the headgear panel.
                with self.goto_equipment(collapsed=False, top=True, equipment_tab=EquipmentTab.HEADGEAR):
                    _found = False,
                    _point = None

                    # Search for the proper locked equipment that matches the current parsed hero.
                    # Swapping headgear if possible.
                    for gear_locations in self.regions.gear_parse:
                        gear = {
                            _newest: False,
                            "equip": None,
                            "locked": False,
                            "equipped": False
                        }

                        # Looping through each location key and region value for in game equipment.
                        # Gear must meet requirements to be specified as valid.
                        for location, region in gear_locations.items():
                            if location == "base":
                                gear["equipped"] = not self._search(image=self.images.equipment_equip, region=region)
                            elif location == "locked":
                                gear["locked"] = self._search(image=self.images.equipment_locked, region=region)
                            elif location == "bonus":
                                # Looking for the bonus or gear stat for the newest hero's type.
                                # ie: Melee newest hero should look for gear with melee damage.
                                gear[_newest] = self._search(image=getattr(self.images, "bonus_{newest}".format(newest=_newest)), region=region)
                            elif location == "equip":
                                # Include click region for equip in data dictionary
                                # for current piece of gear.
                                gear["equip"] = region

                            # Gear is not locked or of proper type.
                            # Continue instead of using this gear.
                            if not gear["locked"] or not gear[_newest]:
                                continue
                            else:
                                if gear["equipped"]:
                                    _found, _point = True, "EQUIPPED"
                                else:
                                    _found, _point = True, gear["equip"]

                                # Break out of the loop now that we have found the proper gear
                                # and know whether or not we need to equip it.
                                break

                        # If no headgear could be found of the needed type that meets the criteria,
                        # we can exit early without equipping anything.
                        if not _found:
                            self.logger.warn("no locked headgear of type: {newest} could be found, skipping headgear swap.".format(newest=_newest))
                            self.calculate_next_headgear_swap()
                            return

                        # Gear of certain index has been found, based on this, we can equip the gear
                        # if it is not already equipped.
                        if isinstance(_point, tuple):
                            self.logger.info("headgear of type: {newest} was found, equipping now.".format(newest=_newest))
                            self.click(point=_point, pause=1)
                        else:
                            if _point == "EQUIPPED":
                                self.logger.info("headgear of type: {newest} is already equipped, skipping headgear swap.".format(newest=_newest))

    @bot_property(forceable=True, calculate="calculate_next_miscellaneous_actions", tooltip="Force all miscellaneous actions in game.", transition=True)
    def miscellaneous_actions(self, force=False):
        """
        Activate and execute all miscellaneous actions in game.
        """
        if force or datetime.now() > self.properties.next_miscellaneous_actions:
            self.logger.info("{begin_or_force} miscellaneous actions process in game now.".format(
                begin_or_force="running" if not force else "forcing"))

            # Begin running through and executing all of our generic functions.
            self.clan_crate()
            self.daily_rewards()
            self.hatch_eggs()
            self.inbox()

    @bot_property(forceable=True, shortcut="shift+b", tooltip="Force a break to take place in game.", transition=True)
    def breaks(self, force=False):
        """
        Perform all break related functionality, pausing all functionality while a break is in progress and waiting.
        """
        if self.configuration.enable_breaks:
            # Grab a reference to the current datetime.
            _now = datetime.now()

            if force or _now > self.properties.next_break:
                # A break can now take place successfully.
                _time_break = self.properties.next_break - _now
                _time_resume = self.properties.break_resume - _now
                # Create a delta that represents how long the break should be.
                _delta = _time_resume - _time_break

                # If the break is just being forced, we should modify the break values to the current
                # datetime plus whatever the most recent break was calculated as.
                if force:
                    self.properties.next_break = _now
                    self.properties.break_resume = _now + _delta

                # Modifying all our "next_" attributes to take place after their normal
                # calculated time with a bit of padding after a break has finished.
                for prop in [prop for prop in self.properties.fields if prop.split("_")[0] == "next" and prop not in [
                    # Ignore any of these properties, since they should not be modified
                    # through the break process.
                    "next_break", "next_raid_attack_reset", "next_artifact_upgrade"
                ]]:
                    _value = getattr(self.properties, prop, None)
                    # Is the value currently setting to something valid that we can change?
                    if _value:
                        # Add padding to the next activation value.
                        setattr(self.properties, prop, _value + _delta + timedelta(seconds=30))

                # Create the initial log datetime, we use this to determine how often
                # a log should be outputted with information about when the bot will be resumed.
                _log_dt = _now
                _log_delta = timedelta(seconds=60)

                while True:
                    _now = datetime.now()

                    # Our break is now over, current datetime has surpassed the configured
                    # break resume datetime.
                    if _now > self.properties.break_resume:
                        self.logger.info("break is now over, resuming bot functionality now.")
                        self.calculate_next_break()
                        return True

                    # Break is not over yet, but we have waited long enough to output a log entry
                    # about how much time is remaining.
                    elif _now > _log_dt:
                        self.logger.info("waiting for break to finish... ({end})".format(end=format_delta(delta=self.properties.break_resume - _now)))
                        _log_dt = _now + _log_delta

                    time.sleep(1)

    @bot_property(forceable=True, calculate="calculate_next_daily_achievement_check", shortcut="ctrl+d", tooltip="Force a daily achievement check in game.", transition=True)
    def daily_achievements(self, force=False):
        """
        Perform a check for any completed daily achievements in game, collecting until no more are available.
        """
        if self.configuration.enable_daily_achievements:
            if force or datetime.now() > self.properties.next_daily_achievement_check:
                self.logger.info("{begin_or_force} daily achievement collection process in game now.".format(begin_or_force="running" if not force else "forcing"))

                with self.goto_master():
                    with self.leave_boss():
                        # Open our achievements panel in game.
                        self.click(point=self.locations.master_achievements, pause=2)

                        # Are there any completed daily achievements available on the screen?
                        # Note: The single "ad watch" daily is not completed here.
                        while self._search(image=self.images.achievement_daily_collect):
                            self.find_and_click(image=self.images.achievement_daily_collect, pause=0.5, log="completed daily achievement found, collecting...")

                        # Additionally, let's look for the vip collection option being
                        # available or not.
                        self.find_and_click(image=self.images.achievement_vip_daily_collect, pause=0.5, log="vip daily achievement found, collecting...")

                        # Existing the achievements panel now, functionality has been completed.
                        self.click(point=self.locations.master_screen_top, clicks=3)

    @bot_property(forceable=True, calculate="calculate_next_milestone_check", shortcut="ctrl+m", tooltip="Force a milestone check to take place in game.", transition=True)
    def milestones(self, force=False):
        """
        Perform a check for any completed milestones that are available.
        """
        if self.configuration.enable_milestones:
            if force or datetime.now() > self.properties.next_milestone_check:
                self.logger.info("{begin_or_force} milestone collection process in game now.".format(begin_or_force="running" if not force else "forcing"))

                if not self.goto_master():
                    return
                if not self.leave_boss():
                    return

                # Open the milestones panel in game.
                self.click(point=self.locations.master_achievements, pause=2)
                self.click(point=self.locations.milestones_header, pause=1)

                # Loop indefinitely until no more milestones can be collected.
                while True:
                    # Milestone collection is available,
                    # collect and wait.
                    if self._is_color(point=self.locations.milestones_collect, color=Color.COLLECT_GREEN):
                        self.logger.info("completed milestone found, collecting now...")
                        self.click(point=self.locations.milestones_collect, pause=1)
                        self.click(point=self.locations.game_middle, clicks=5, interval=0.5)
                        # Wait for a little while after collecting the milestone.
                        time.sleep(3)

                    # Otherwise, no milestones are actually available to be completed
                    # at this time.
                    else:
                        self.logger.info("no milestones are available for completion.")
                        break

                # Exiting the milestones panel now, functionality has been completed.
                self.click(point=self.locations.master_screen_top, clicks=3)

    @bot_property(forceable=True, calculate="calculate_next_raid_notifications_check", shortcut="ctrl+r", tooltip="Force a raid notification check in game.", transition=True)
    def raid_notifications(self, force=False):
        """
        Perform all checks to see if a notification will be generated when clan raid attacks are available.
        """
        if self.configuration.enable_raid_notifications:
            if force or datetime.now() > self.properties.next_raid_notifications_check:
                self.logger.info("{begin_or_force} milestone collection process in game now.".format(begin_or_force="running" if not force else "forcing"))

                # Has an attack reset value already been parsed out?
                # In which case, we should just return early and recalculate
                # the next time we should check for raid notifications.
                if self.properties.next_raid_attack_reset and self.properties.next_raid_attack_reset > datetime.now():
                    self.logger.info("the next raid attack reset is still pending, no notification will be sent.")
                    self.calculate_next_raid_notifications_check()
                    return

                # Open up the clan raid panel and check if the bight button is available,
                # This would mean that we can fight the boss. If it is present, we also want to check
                # how much time until attacks are reset, once the time has surpassed, we can send another.
                if not self.goto_clan():
                    return

                self.click(point=self.locations.clan_raid, pause=4)

                # Check that the fight button is available within the clan raid panel.
                if self._search(image=self.images.raid_fight):
                    # Fights are available, begin parsing out the next time that attack
                    # resets will be ready again.
                    _result = pytesseract.image_to_string(
                        image=self._process(scale=3, region=self.regions.raid_attack_reset, use_current=True),
                        config="--psm 7"
                    )

                    # Attempt to parse out the timedelta from the text grabbed through the clan
                    # raid attack resets value. Result here may look like: "Attack reset in: 3d 5h 10m".
                    _result = delta_from_value_string(value=_result.split(" ")[3:])

                    # Set our delta properly to the result we've parsed,
                    # regardless of the status of the parse.
                    self.properties.next_raid_attack_reset = _result

                    # Send out a notification about the raid attacks being available now.
                    # ...
                    # ...

                # Otherwise, attacks are not currently available for whatever reason,
                # Just log this and continue.
                else:
                    self.logger.info("no raid attacks are active or available, notification will not be sent.")

    @bot_property(forceable=True, calculate="calculate_next_fairy_tap", tooltip="Force tapping process to try and click on fairies in game.", transition=True)
    def fairy_tap(self, force=False):
        """
        Perform in game tapping process.
        """
        if force or datetime.now() > self.properties.next_fairy_tap:
            self.logger.info("beginning fairy tapping process.")

            with self.ensure_collapsed():
                # Looping through all of the fairy map locations points. Clicking and
                # checking for ads throughout the process.
                for index, point in enumerate(self.locations.game_fairies_map, start=1):
                    self.click(point=point)

                    # Every fifth click, we want to check quickly to see if an ad was pressed
                    # on which could potentially open a fairy ad.
                    if index % 5 == 0:
                        self.collect_ad_no_transition()

                # Wait slightly after clicking has taken place to ensure that
                # any delayed fairy ads are ready when the next transition state is checked.
                time.sleep(1)

    @bot_property(forceable=True, calculate="calculate_next_minigames_tap", tooltip="Force minigame tapping process in game.", transition=True)
    def minigames(self, force=False):
        """
        Perform in game minigame tapping process.
        """
        if self.configuration.enable_minigames:
            if force or datetime.now() > self.properties.next_minigame_tap:
                self.logger.info("beginning minigame tapping process.")

                with self.ensure_collapsed():
                    _tapping_map = []
                    # Based on the minigames currently enabled, we can create a list
                    # of tapping locations that will be looped through and tapped on.
                    for minigame in self.minigame_order:
                        # Add (str) to the map when for each one, we check for this while
                        # looping so we can also output a log message about the minigame.
                        _tapping_map += (minigame,)
                        _tapping_map += getattr(self.locations, "minigame_{minigame}".format(minigame=minigame))

                    self.logger.info("executing minigames tapping process {repeats} time(s).".format(repeats=self.configuration.repeat_minigames))

                    # Looping through all of the minigame tapping location points. Clicking and
                    # checking for ads throughout the process.
                    for i in range(self.configuration.repeat_minigames):
                        for index, point in enumerate(_tapping_map, start=1):
                            if isinstance(point[0], str):
                                self.logger.info("performing {minigame} taps now.".format(minigame=point))
                            # Perform proper minigame point click here.
                            # Only when the point is not a string instance.
                            else:
                                self.click(point=point)

                            # Every fifth click, we should check to see if an ad is present on the
                            # screen now, since our clicks could potentially trigger a fairy ad.
                            if index % 5 == 0:
                                self.collect_ad_no_transition()

                    # Wait slightly after clicking has taken place to ensure that
                    # any delayed fairy ads are ready when the next transition state is checked.
                    time.sleep(2)

    @bot_property(queueable=True, tooltip="Attempt parse out all owned artifacts from in game.", transition=True)
    def parse_artifacts(self):
        """
        Begin the artifact parsing process in game.
        """
        def _duplicate(image_one, image_two, cutoff=2):
            """
            Determine if the images specified are duplicates.
            """
            return average_hash(image=image_one) - average_hash(image=image_two) < cutoff

        def _parse_image(_artifacts, _image):
            """
            Given an image, attempt to search for our any artifacts present within.
            """
            _locally_found = []

            for artifact in _artifacts:
                # Skip iteration if we've already found this artifact.
                if artifact.artifact.name in _found:
                    continue

                # Get a cv2 resized version of the artifact being looked for.
                # Smaller images will make our search functionality go faster.
                artifact_image = cv2.imread(filename=ARTIFACTS[artifact.artifact.name])
                artifact_image = cv2.resize(src=artifact_image, dsize=None, fx=0.5, fy=0.5)

                if self._search(image=artifact_image, im=_image, image_name=artifact.artifact.name):
                    if artifact.artifact.name not in _locally_found:
                        self.logger.info("artifact: {artifact} has been found.".format(artifact=artifact.artifact.name))
                        _locally_found.append(artifact.artifact.name)

            # If we've found any artifacts, we can add them to the list of globally
            # found artifacts so far.
            if _locally_found:
                _found.extend(_locally_found)

        self.logger.info("beginning artifact parsing process in game now.")

        # Ensure we are not in any boss fights in game while parsing takes place.
        with self.leave_boss():
            with self.goto_artifacts(collapsed=False):
                # Begin with both empty variables for our
                # local threads and found artifacts.
                _threads = []
                _found = []

                # Take an initial screenshot of the artifacts panel.
                # We need at least one before performing duplicate checks.
                self._snapshot(region=self.regions.artifact_parse, downsize=0.5)

                # Create the initial list that will be used to place image
                # objects into it from our snapshots.
                _container = [self._last_snapshot]

                # Looping forever until we break from our loop due to a duplicate
                # image being found, or the max amount of loops being hit.
                loops = 0

                # Begin a loop that will take photos of different artifact panel
                # images after performing drags to find different owned artifacts.
                while loops != Timeout.FUNCTION_TIMEOUT.value:
                    loops += 1

                    # Only dragging after our initial snapshot is taken
                    # and parsing begins on the top image available.
                    if loops > 1:
                        self.drag(start=self.locations.game_scroll_start, end=self.locations.game_scroll_bottom_end)

                    # Wait slightly after each drag, otherwise our images could potentially
                    # never find duplicates the image is taken while the drag is in progress.
                    time.sleep(1.5)

                    self._snapshot(region=self.regions.artifact_parse, downsize=0.5)

                    # Make sure we didn't just take a duplicate image. Which would mean we should
                    # break out of our loop so that we can begin collecting threads.
                    if loops > 1 and _duplicate(image_one=self._last_snapshot, image_two=_container[-1]):
                        # Duplicate images found means we should have a list with all possible
                        # artifact panel drags.
                        break

                    # Otherwise, we can add our current image to the list of all artifact
                    # panel images and keep looping.
                    else:
                        _thread = threading.Thread(
                            target=_parse_image,
                            kwargs={
                                "_artifacts": self.statistics.artifact_statistics.unowned(),
                                "_image": self._last_snapshot
                            }
                        )
                        # Ensure we also add our image to our image container,
                        # this allows us to properly check for duplicates.
                        _container.append(self._last_snapshot)
                        # Start out thread and append it to our list
                        # of threads, they can all be joined together afterwards.
                        _thread.start()
                        _threads.append(_thread)

                # Join all of our threads, with parsed artifact information.
                # They start running above as soon as they are created.
                for thread in _threads:
                    thread.join()

                self.logger.info("successfully found {found} artifacts in game.".format(found=len(_found)))

                # Update our bots artifact statistics now that
                # we should have all found artifact in one variable.
                self.statistics.artifact_statistics.artifacts.filter(artifact__name__in=_found).update(owned=True)

    @bot_property(queueable=True, shortcut="shift+a", tooltip="Begin the artifact discovery/enchantment/purchase process in game.", transition=True)
    def artifacts(self):
        """
        Run the artifact purchasing process in game, handling discovery, enchantment and purchasing (upgrade).
        """
        def _discover_or_enchant(_image, point, color):
            """
            Determine whether or not an artifact discovery/enchantment can be performed.
            """
            if self._search(image=_image) and self._is_color(point=point, color=color):
                # Image is available and the color is proper to allow for the discovery or enchant.
                # Ensure we click on the point and confirm purchase, followed by clicking to skip preview.
                self.click(point=point, pause=1)
                self.click(point=self.locations.artifact_purchase, pause=2)
                self.click(point=self.locations.panel_close_top, clicks=5, interval=0.5, pause=2)

        # Does the configuration even allow for artifact discovery or enchantment as this point?
        # If so, attempt proper to find any of the options.
        if self.configuration.enable_artifact_discover_enchant:
            with self.goto_artifacts():
                self.logger.info("attempting to discover and enchant artifacts if available.")
                # Check for both the ability to either discover a new
                # artifact, or enchant one that's already owned.
                _discover_or_enchant(_image=self.images.artifact_discover, point=self.locations.artifact_discover, color=Color.DISCOVER)
                _discover_or_enchant(_image=self.images.artifact_enchant, point=self.locations.artifact_enchant, color=Color.ENCHANT)

        # Does the configuration allow for artifact purchasing (upgrades),
        # If so, attempt to setup the artifacts panel to prepare for purchase.
        if self.configuration.enable_artifact_upgrade:
            with self.goto_artifacts():
                _upgrade = self.properties.next_artifact_upgrade

                # We have a reference to the artifact being upgraded,
                # we can update the next one while we're here.
                self.update_next_artifact_purchase()

                self.logger.info("attempting to upgrade artifact: {artifact} now.".format(artifact=_upgrade))

                # Ensure proper spending settings are configured before actually upgrading
                # the artifact or scrolling to find it.

                # 1. Ensure that the percentage (%) multiplier is selected for artifacts.
                while not self._search(image=self.images.artifact_percent_on, precision=0.9):
                    self.click(point=self.locations.artifact_percent_toggle, pause=0.5)
                # 2. Ensure that the spend max multiplier is selected for artifacts.
                while not self._search(image=self.images.artifact_spend_max, precision=0.9):
                    self.click(point=self.locations.artifact_buy_multiplier, pause=0.5)
                    self.click(point=self.locations.artifact_buy_max, pause=0.5)

                # Begin searching for the actual artifact that will be upgraded,
                # dragging the panel each time it is not found.
                image = getattr(self.images, _upgrade)
                loops = 0
                found = False

                while loops != Timeout.FUNCTION_TIMEOUT.value and not found:
                    # Looping until we've reached our function timeout limit and while
                    # the artifact in question has not been found.
                    loops += 1

                    found = self.find_and_click(
                        image=image,
                        precision=0.7,
                        padding=(self.locations.artifact_push_x, self.locations.artifact_push_y),
                        log="artifact: {artifact} has been found, upgrading now.".format(artifact=_upgrade)
                    )

                    # If the image wasn't found and clicked, let's drag our panel slightly
                    # before attempting to try again.
                    if not found:
                        self.drag(start=self.locations.game_scroll_start, end=self.locations.game_scroll_bottom_end, pause=1.5)

                # No artifact was found after looping, we can skip the purchase process and log a warning
                # about the issue.
                if not found:
                    self.logger.warn("unable to find artifact: {artifact}, skipping purchase.".format(artifact=_upgrade))

    @bot_property(queueable=True, shortcut="shift+d", tooltip="Check for daily rewards in game and collect them if available.", transition=True)
    def daily_rewards(self):
        """
        Collect any daily rewards in game if they're currently available.
        """
        self.logger.info("attempting to collect daily rewards if they are available.")

        with self.ensure_collapsed():
            # Attempting to click on the location where daily rewards would be present
            # if they are available.
            self.click(point=self.locations.rewards_open, pause=0.5)

            if self._search(image=self.images.rewards_header):
                # Rewards are available, or at least, the panel opened, let's go through
                # the normal flow to collect the gifts.
                self.click(point=self.locations.rewards_collect, pause=1)
                self.click(point=self.locations.game_middle, clicks=5, interval=0.5, pause=1)
                self.click(point=self.locations.master_screen_top, pause=1)

    @bot_property(queueable=True, tooltip="Check for available eggs in game and hatch them.", transition=True)
    def hatch_eggs(self):
        """
        Hatch any eggs in game if they are currently available.
        """
        if self.configuration.enable_eggs:
            self.logger.info("attempting to collect and hatch eggs if they are available.")

            with self.ensure_collapsed():
                self.click(point=self.locations.eggs_hatch, pause=0.5)
                self.click(point=self.locations.game_middle, clicks=5, interval=0.5, pause=1)

    @bot_property(queueable=True, tooltip="Check for a clan crate in game and collect them if available.", transition=True)
    def clan_crate(self):
        """
        Check for an available clan crate in game and collect it.
        """
        self.logger.info("attempting to collect clan crates if they are available.")

        with self.ensure_collapsed():
            # Looping a couple of times in case something is in front of the clan crate
            # or the click is not registered.
            for i in range(5):
                # Try to click on the location where clan crate would be if one was available.
                self.click(point=self.locations.game_collect_clan_crate, pause=1)

                # A confirmation will be present if a clan crate is present,
                # find and click that to collect.
                if self.find_and_click(image=self.images.crate_okay, pause=1):
                    return

    @bot_property(queueable=True, tooltip="Clear out any inbox notifications in game.", transition=True)
    def inbox(self):
        """
        Open up the inbox if it's available on the screen in game, attempting to clear notifications.
        """
        self.logger.info("attempting to clear our inbox notifications in game.")

        with self.ensure_collapsed():
            self.click(point=self.locations.inbox_icon, pause=0.5)

            # Check for the inbox headers presence, we only actually open the inbox
            # panel when a notification is there that we haven't checked yet.
            if self._search(image=self.images.inbox_header):
                # Iterate a small amount so we get some variability in the
                # header swapping, ensuring our notifications are "read".
                for i in range(2):
                    for location in [self.locations.inbox_clan, self.locations.inbox_news]:
                        self.click(point=location, pause=0.2)

                # Close the inbox screen now once we've handled the checking
                # of notifications.
                self.click(point=self.locations.master_screen_top, clicks=3, interval=0.2, pause=0.5)

    @bot_property(queueable=True, shortcut="shift+f", tooltip="Attempt to fight a boss in game.", wrap_name=False, transition=True)
    def fight_boss(self):
        """
        Attempt to enter a boss fight in game.
        """
        try:
            if self._search(image=self.images.no_panel_fight_boss):
                # Loop until our boss loop timeout has been reached, or we've
                # successfully found and clicked on the fight boss button.
                loops = 0

                while loops != Timeout.BOSS_TIMEOUT.value:
                    loops += 1

                    if self.find_and_click(image=self.images.no_panel_fight_boss, pause=0.8, log="initiating boss fight in game now."):
                        break

                    # Boss fight wasn't found and clicked on yet, wait a little while
                    # before attempting to enter the boss fight again.
                    time.sleep(0.5)

            # Yield true once we've either found the image and
            # broken out of our loop, or the fight boss image was never present.
            yield True
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, shortcut="shift+l", tooltip="Attempt to leave a boss fight in game.", wrap_name=False, transition=True)
    def leave_boss(self):
        """
        Attempt to leave a boss fight in game.
        """
        try:
            if self._search(image=self.images.no_panel_leave_boss):
                # Loop until our boss loop timeout has been reached, or we've
                # successfully found and clicked on the leave boss button.
                loops = 0

                while loops != Timeout.BOSS_TIMEOUT.value:
                    loops += 1
                    # Look for the leave boss icon in game and attempt
                    # to click it.
                    if not self.find_and_click(image=self.images.no_panel_leave_boss, pause=0.8, log="leaving boss fight in game now."):
                        break

                    # Leave boss fight wasn't found and clicked on yet, wait a little while
                    # before attempting to enter the boss fight again.
                    time.sleep(0.5)

            # Yield true once we've either found the image and
            # broken out of our loop, or the leave boss image was never present.
            yield True
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, tooltip="Ensure that the game panels are collapsed.", wrap_name=False, transition=True)
    def ensure_collapsed(self):
        """
        Ensure that the current panel is collapsed, regardless of which panel is currently open.
        """
        try:
            # If we reach this point, it means that our images are not yet available,
            # attempt to collapse whatever panel is currently open.
            loops = 0
            # Looping until we reach our function loop timeout, attempting to find and
            # click on any collapse panels.
            _found = False
            while loops != Timeout.FUNCTION_TIMEOUT.value:
                loops += 1
                # Look for a collapsible icon somewhere in the game and try to click it.
                # Once pressed, we know that we are now collapsed.
                if self.find_and_click(image=self.images.generic_collapse_panel, pause=1):
                    _found = True
                    break
                # Look for any of these generic images, we can use these to derive
                # whether or not panels are collapsed.
                if self._search(image=[self.images.no_panel_settings, self.images.no_panel_clan_raid_ready, self.images.no_panel_clan_no_raid]):
                    _found = True
                    break

                if not _found:
                    # None of the valid images were found or clicked,
                    # Sleep slightly before continuing.
                    time.sleep(1)

            if _found:
                yield True
            else:
                # If we reach this point, the game has frozen or our
                # shop panel is open, simply try to close the open panel instead.
                with self.no_panel():
                    yield True
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, tooltip="Ensure that no panels are open in game.", wrap_name=False, transition=True)
    def no_panel(self):
        """
        Ensure that no panels in game are currently open.
        """
        try:
            while self._search(image=self.images.generic_exit_panel):
                loops = 0
                # Looping until we reach our function loop timeout, attempting to find and
                # click on any generic panels found.
                while loops != Timeout.FUNCTION_TIMEOUT.value:
                    loops += 1
                    # Look for the exit panel image somewhere and try to click it.
                    # Once pressed, we know that no panel is open.
                    if self.find_and_click(image=self.images.generic_exit_panel, pause=0.5):
                        break
                    # Look for any of these generic images, we can use these to derive
                    # whether or not panels are collapsed.
                    if self._search(image=[self.images.no_panel_pet_damage, self.images.no_panel_master_damage]):
                        break

            # Yield true as soon as we find and click
            # on the exit panel or we find the generic images.
            yield True
        finally:
            pass

    def _goto_panel(self, panel, icon, top_find, bottom_find, collapsed=True, top=True, equipment_tab=None):
        """
        Attempt to travel to the top or bottom of the specified panel in a collapsed or un-collapsed state.
        """
        self.logger.debug("attempting to travel to the {collapse_or_expand} {top_or_bottom} of {panel} panel.".format(
            collapse_or_expand="collapsed" if collapsed else "expanded",
            top_or_bottom="top" if top else "bottom",
            panel=panel.value
        ))

        loops = 0

        # Begin initial while loop to try and just ensure that the specified panel
        # is open and active.
        while not self._search(image=icon):
            # Maybe we're unable to get into this panel for some reason,
            # likely that the game might have froze, exit early.
            if loops == Timeout.FUNCTION_TIMEOUT.value:
                return False

            loops += 1

            # Attempt to click on and open the specified panel location
            # by clicking on the bottom bar location for the specified panel.
            self.click(point=getattr(self.locations, "bottom_{panel}".format(panel=panel.value)), pause=1)

        # The shop panel can not be expanded/collapsed, skip that process when trying to
        # open the shop panel in game.
        if panel.value != Panel.SHOP.value:
            # Ensure the panel is expanded or collapsed appropriately
            # through a while loop with max loops.
            loops = 0
            image = self.images.generic_expand_panel if collapsed else self.images.generic_collapse_panel
            point = self.locations.panel_expand_or_collapse_top if collapsed else self.locations.panel_expand_or_collapse_bottom

            # Begin while loop to try and expand or collapse the specified panel.
            while not self._search(image=image):
                # If we're unable to expand or collapse, it's likely that
                # the game has froze, exit early.
                if loops == Timeout.FUNCTION_TIMEOUT.value:
                    return False

                loops += 1

                # Attempt to click on the derived expand / collapse location.
                self.click(point=point, pause=1, offset=1)

        # Equipment pane acts slightly different then other panels, there is not really a top
        # or bottom of this panel, but we can choose between the different equipment types to travel to.
        if panel.value == Panel.EQUIPMENT.value:
            if not equipment_tab:
                return True

            # Ensure that the specified tab is opened within the equipment panel.
            # ie: sword, headgear, cloak, aura, slash.
            click = getattr(self.locations, "equipment_tab_{tab}".format(tab=equipment_tab.value))
            start = self.locations.equipment_drag_start if top else self.locations.equipment_drag_end
            end = self.locations.equipment_drag_end if top else self.locations.equipment_drag_start

            # Ensure that the specified tab has been clicked on within the equipment panel.
            self.click(point=click, clicks=5, interval=0.5)
            # Drag a little but to ensure that the top or bottom of the panel is travelled to.
            self.drag(start=start, end=end)

        # Any other panel travelling will take place here.
        # Panel should at least be opened at this point.
        else:
            loops = 0
            find = top_find if top or bottom_find is None else bottom_find
            end = self.locations.game_scroll_top_end if top else self.locations.game_scroll_bottom_end

            # Trying to travel to the top or bottom of the specified panel now.
            # Looping until we reach the max loops or successfully get to top or bottom.
            while not self._search(image=find):
                if loops == Timeout.FUNCTION_TIMEOUT.value:
                    # Unable to travel to the top or bottom of the panel,
                    # game may of froze or issue with icons, exit early.
                    return False

                loops += 1

                # Attempt to drag our panel to the top or bottom of the panel,
                # depending on the arguments provided.
                self.drag(start=self.locations.game_scroll_start, end=end, pause=1)

        # Reaching this point represents that the specified panel
        # was successfully reached in the game.
        return True

    @contextmanager
    @bot_property(queueable=True, tooltip="Attempt to travel to the sword master panel in game.", wrap_name=False, transition=True)
    def goto_master(self, collapsed=True, top=True):
        """
        Attempt to travel the the sword master panel in game.
        """
        try:
            yield self._goto_panel(
                panel=Panel.MASTER,
                icon=self.images.generic_master_active,
                top_find=self.images.master_raid_cards,
                bottom_find=self.images.master_silent_march,
                collapsed=collapsed,
                top=top
            )
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, tooltip="Attempt to travel to the heroes panel in game.", wrap_name=False, transition=True)
    def goto_heroes(self, collapsed=True, top=True):
        """
        Attempt to travel to the heroes panel in game.
        """
        try:
            yield self._goto_panel(
                panel=Panel.HEROES,
                icon=self.images.generic_heroes_active,
                top_find=self.images.hero_masteries,
                bottom_find=self.images.hero_maya_muerta,
                collapsed=collapsed,
                top=top
            )
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, tooltip="Attempt to travel to the equipment panel in game.", wrap_name=False, transition=True)
    def goto_equipment(self, collapsed=True, top=True, equipment_tab=None):
        """
        Attempt to travel to the equipment panel in game.
        """
        try:
            yield self._goto_panel(
                panel=Panel.EQUIPMENT,
                icon=self.images.generic_equipment_active,
                top_find=None,
                bottom_find=None,
                collapsed=collapsed,
                top=top,
                equipment_tab=equipment_tab
            )
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, tooltip="Attempt to travel to the pets panel in game.", wrap_name=False, transition=True)
    def goto_pets(self, collapsed=True, top=True):
        """
        Attempt to travel to the pets panel in game.
        """
        try:
            yield self._goto_panel(
                panel=Panel.EQUIPMENT,
                icon=self.images.generic_pets_active,
                top_find=self.images.pet_next_egg,
                bottom_find=None,
                collapsed=collapsed,
                top=top
            )
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, tooltip="Attempt to travel to the artifacts panel in game.", wrap_name=False, transition=True)
    def goto_artifacts(self, collapsed=True, top=True):
        """
        Attempt to travel to the artifacts panel in game.
        """
        try:
            yield self._goto_panel(
                panel=Panel.ARTIFACTS,
                icon=self.images.generic_artifacts_active,
                top_find=self.images.artifact_salvaged,
                bottom_find=None,
                collapsed=collapsed,
                top=top
            )
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, tooltip="Attempt to travel to the shop panel in game.", wrap_name=False, transition=True)
    def goto_shop(self, collapsed=False, top=True):
        """
        Attempt to travel to the shop panel in game.
        """
        try:
            yield self._goto_panel(
                panel=Panel.SHOP,
                icon=self.images.generic_shop_active,
                top_find=self.images.shop_keeper,
                bottom_find=None,
                collapsed=collapsed,
                top=top
            )
        finally:
            pass

    @contextmanager
    @bot_property(queueable=True, tooltip="Attempt to open the clan panel in game.", wrap_name=False, transition=True)
    def goto_clan(self):
        """
        Open the clan panel in game.
        """
        try:
            self.logger.info("attempting to open the clan panel in game.")
            # Looping indefinitely until we've opened up the clan panel,
            # or we've reached our function loop timeout.
            loops = 0

            while not self._search(image=self.images.clan_header):
                loops += 1
                # Loops have reached the allowed limit, in which case,
                # we should just give up trying to open the panel.
                if loops == Timeout.FUNCTION_TIMEOUT:
                    yield False

                self.click(point=self.locations.clan_icon)

                # Wait slightly after attempting to open the clan panel.
                time.sleep(3)
            # Reaching this point means we definitely reached the clan panel.
            # Just yield a truthy variable.
            yield True
        finally:
            pass

    @bot_property(queueable=True, shortcut="p", tooltip="Pause bot functionality.")
    def pause(self):
        """
        Attempt to pause the current bot instance.
        """
        self._should_pause = True

        # Send a pause signal to the instance associated
        # with this bot.
        self.instance.pause()

        # Make sure we also pause our function scheduler
        # if it is currently running.
        if self.scheduler.state == STATE_RUNNING:
            self.scheduler.pause()

    @bot_property(queueable=True, shortcut="r", tooltip="Resume all bot functionality.")
    def resume(self):
        """
        Attempt to resume the current bot instance.
        """
        self._should_pause = False

        # Send a resume signal to the instance associated
        # with this bot.
        self.instance.resume()

        # Make sure we also resume our function scheduler
        # if it is currently running.
        if self.scheduler.state == STATE_PAUSED:
            self.scheduler.resume()

    @bot_property(queueable=True, shortcut="e", tooltip="Terminate all bot functionality.")
    def terminate(self):
        """
        Attempt to terminate the current bot instance.
        """
        self._should_terminate = True

        # Send a stop signal to the instance associated
        # with this bot.
        self.instance.stop()

    @bot_property(queueable=True, tooltip="Collect a fairy ad in game if one is available.", transition=True)
    def collect_ad(self):
        """
        Collect an ad if one is available with transition checks included.
        """
        self.ad()

    def collect_ad_no_transition(self):
        """
        Collect an ad if one is available without transition checks included.
        """
        self.ad()

    def ad(self):
        """
        Collect an ad if one is available and present in the game.
        """
        _collected = False

        while self._search(image=[self.images.ad_collect, self.images.ad_watch]):
            # Can we just simply find and click the vip collection button
            # before trying anything else?
            _collected = self.find_and_click(image=self.images.ad_collect, pause=1)

            if not _collected:
                # Unable to use vip to collect the ad, we can attempt
                # some additional alternative methods instead.
                if _globals.pihole_enabled():
                    self.logger.info("attempting to collect ad with pi hole now...")

                    # Pi hole is enabled, wait until a collect button has shown up
                    # on the screen after beginning the watching process.
                    while not self._search(image=self.images.ad_collect):
                        self.find_and_click(
                            image=self.images.ad_watch,
                            pause=2,
                            log="waiting for pi hole to finish watching ad..."
                        )

                    # Ad has finished processing at this point, the collect ad button
                    # should now be present on the screen.
                    _collected = self.find_and_click(image=self.images.ad_collect, pause=1)

                # Pi hole function is disabled, we should just simply decline the ad
                # and continue with normal functionality.
                else:
                    self.find_and_click(image=self.images.ad_no_thanks, pause=1, log="declining fairy ad now.")

        if _collected:
            self.logger.info("ad was successfully collected.")
            # Update and increment the current number of ads collected
            # for this bot instance and save.
            self.statistics.bot_statistics.ads_collected += 1
            self.statistics.bot_statistics.save()

    def welcome_screen_check(self):
        """
        Check to see if the welcome panel is currently on the screen and attempt to close it.
        """
        if self._search(image=self.images.welcome_header):
            # Welcome header is present, try and collect through non vip
            # means first.
            if not self.find_and_click(image=self.images.welcome_collect_no_vip, pause=1):
                # Try to use vip collection if the first method
                # does not work properly.
                self.find_and_click(image=self.images.welcome_collect_vip, pause=1)

    def rate_screen_check(self):
        """
        Check to see if the game rate panel is currently open on the screen and attempt to close it.
        """
        if self._search(image=self.images.rate_icon):
            # Attempt to close the rate screen if one is
            # open in the game currently.
            self.find_and_click(image=self.images.rate_icon, pause=1)

    def hook_shortcuts(self):
        """
        Setup and hook the keypress listener for this bot instance.
        """
        self.logger.info("initializing and hooking keypress listener.")

        # Generate the keypress handle for this bot instance.
        shortcuts_handler.add_handler(instance=self.instance, logger=self.logger)
        # Attempt to hook to keypress listener for this bot instance.
        shortcuts_handler.hook()

    def setup_loop_functions(self):
        """
        Generate a list of loop functions based on the enabled functions present in the configuration.
        """
        # Using function.__name__ to ensure that changing functions will cause this to error out
        # we know that we need to update this.
        _lst = [
            k for k, v in {
                self.fight_boss.__name__: True,
                self.miscellaneous_actions.__name__: True,
                self.fairy_tap.__name__: True,
                self.minigames.__name__: self.configuration.enable_minigames,
                self.level_master.__name__: self.configuration.enable_master,
                self.level_heroes.__name__: self.configuration.enable_heroes,
                self.level_skills.__name__: self.configuration.enable_level_skills,
                self.activate_skills.__name__: self.configuration.enable_activate_skills,
                self.swap_headgear.__name__: self.configuration.enable_headgear_swap,
                self.perks.__name__: self.configuration.enable_perk_usage,
                self.prestige.__name__: self.configuration.enable_auto_prestige,
                self.daily_achievements.__name__: self.configuration.enable_daily_achievements,
                self.milestones.__name__: self.configuration.enable_milestones,
                self.raid_notifications.__name__: self.configuration.enable_raid_notifications,
                self.update_statistics.__name__: self.configuration.enable_statistics,
                self.breaks.__name__: self.configuration.enable_breaks
            }.items() if v
        ]

        self.logger.info("loop functions have been initialized.")
        self.logger.info("functions: {functions}".format(functions=", ".join(_lst)))

        # Return our dynamically generated list of functions that will be
        # used when looping through our main event loop.
        return _lst

    def pre_run(self):
        """
        Run any pre run functionality that should happen before the main event loop takes place.
        """
        # Boot up the scheduler instance so that it begins
        # running all interval based functions.
        if self.scheduler.state == STATE_STOPPED:
            self.scheduler.start()

        # Parse out the current skills from in game.
        # We do this once before starting our run to make
        # sure skills can be levelled properly.
        self.parse_current_skills()

        # Perform some conditional checks to make sure we explicitly run certain
        # functions before the main event loop has begun.
        for func in [
            f for f, enabled in {
                self.level_master: self.configuration.master_level_on_start,
                self.level_heroes: self.configuration.hero_level_on_start,
                self.level_skills: self.configuration.level_skills_on_start,
                self.activate_skills: self.configuration.activate_skills_on_start,
                self.update_statistics: self.configuration.update_statistics_on_start,
                self.daily_achievements: self.configuration.daily_achievements_check_on_start,
                self.milestones: self.configuration.milestones_check_on_start,
                self.raid_notifications: self.configuration.raid_notifications_check_on_start,
                self.swap_headgear: self.configuration.headgear_swap_on_start,
                self.perks: self.configuration.use_perks_on_start
            }.items() if enabled
        ]:
            # Execute each dynamically derived force function that should
            # be ran before anything else is done.
            func(force=True)

    def run(self):
        """
        Run this bot instance, beginning the main event loop that executes all loop functions and checks for queued functions.
        """
        # Local level import of the queued function model.
        # Avoid circular imports.
        from db.models import QueuedFunction

        # Encapsulating everything in a try catch block so that we can check for
        # our own exceptions that should resume/pause or stop bot instances, as well
        # as any exceptions that are thrown during runtime.
        try:
            if self.shortcuts:
                self.hook_shortcuts()

            # Begin all functionality always by running our pre_run function.
            # This handles any forced functions that should be ran first.
            self.pre_run()

            # Let's grab the upgrade artifacts for this bot instance.
            # This is handled once before our main loop.
            self.get_upgrade_artifacts()

            # Let's also make sure we know which artifact is going to be upgraded
            # once a prestige takes place (if enabled).
            if self.configuration.enable_artifact_upgrade:
                self.update_next_artifact_purchase()

            _loop_functions = self.setup_loop_functions()
            _loop_paused_dt = datetime.now() + timedelta(seconds=10)

            while True:
                for _function in _loop_functions:
                    # Grab our floor and ceiling values for any functions executed through
                    # the bot, queued or from our event loop.
                    _wait_floor = self.configuration.post_action_min_wait
                    _wait_ceiling = self.configuration.post_action_max_wait

                    # Explicitly queued functions should be executed (checked) once each time a new loop
                    # function is entered. Ensuring that we "resume" where we left when the queued function
                    # was encountered.
                    for _queued in QueuedFunction.objects.filter(instance=self.instance):
                        # Queued functions should only be ran if the instance
                        # is not in a paused state, a paused bot should only allow
                        # the "resume" function to be executed.
                        if self._should_pause and _queued.function != "resume":
                            # Breaking here if queued function should not be
                            # executed yet. Continuing to normal functionality below.
                            break

                        # Make sure that the queued function encountered actually exists on the bot.
                        # Although this is unlikely, it could occur.
                        if not bot_property.queueables(function=_queued.function, forceables=True):
                            self.logger.warn("queued function: {queued} does not exist as a queueable, ignoring...".format(queued=_queued.function))

                        # Otherwise, the function encountered exists and can be executed.
                        # Go through normal queued function flow.
                        else:
                            self.logger.info("executing queued function: {queued} now.".format(queued=_queued.function))

                            # Generate the decorated callable that will ensure our function
                            # call sleeps for a random amount of time after being called.
                            wait = wait_afterwards(function=getattr(self, _queued.function), floor=_wait_floor, ceiling=_wait_ceiling)

                            # Make sure we use the proper "force" flag for our queued function
                            # if the function is specified as a forceable through our decorator.
                            wait(force=True) if bot_property.forceables(function=_queued.function) else wait()

                        # Regardless of whether or not the functions exists
                        # or not, make sure we "finish" it so it isn't executed again.
                        _queued.remove()

                    # Maybe a termination has been applied to the bot, in which case,
                    # we should go ahead and raise our termination error.
                    if self._should_terminate:
                        # Raising our base termination error.
                        # Ensuring that bot stops functionality.
                        raise TerminationEncountered()

                    # Should the pause state be applied to the bot?
                    # This happens when a user manually pauses the bot
                    # through a queued function call.
                    if self._should_pause:
                        # Perform quick failsafe check just in case,
                        # since we could be in this conditional for a while.
                        _globals.failsafe_check()

                        # Bot is paused when in this function.
                        # Check whether or not a log should be emitted
                        # about us waiting for a resume before continuing.
                        _now = datetime.now()

                        # Current timestamp is greater than the current paused datetime
                        # timestamp, this makes sure we don't emit a log on every execution of this.
                        if _now > _loop_paused_dt:
                            self.logger.info("waiting for bot resume...")

                            # Update the paused datetime log value.
                            # Ten seconds later, another one will be emitted.
                            _loop_paused_dt = _now + timedelta(seconds=10)

                        continue

                    # Just run the loop function normally.
                    # Queued functions are taken care of above.
                    wait_afterwards(function=getattr(self, _function), floor=_wait_floor, ceiling=_wait_ceiling)()

        # The eel server has been terminated and we can end the bot instance
        # correctly to avoid running instances on restarts.
        except ServerTerminationEncountered:
            self.logger.exception("server termination has been encountered, exiting...")
            raise
        # Termination's can be queued up by users and will end execution manually
        # of any bot instances.
        except TerminationEncountered:
            self.logger.exception("manual termination of the bot has been encountered, exiting...")
            raise
        # Failsafe exceptions may occur when they are enabled, and when the
        # use drags their mouse pointer to the top left of the screen during runtime.
        except FailSafeException:
            self.logger.exception("failsafe termination of the bot has been encountered, exiting...")
            raise
        # A base exceptions represents and unknown error that has occurred.
        # These should be rare, but may occur and are worth catching for logging.
        except Exception:
            self.logger.exception("fatal error encountered while bot was running, exiting...")
            raise

        # Make sure we perform any required cleanup after a bot instance
        # has stopped running, regardless of why.
        finally:
            # Stop the function schedulers functionality once
            # the bot session has finished execution.
            if self.scheduler.state in [STATE_RUNNING, STATE_PAUSED]:
                self.scheduler.shutdown(wait=False)

            # Ending the session here, handling the stopped datetime
            # and stopping of the instance itself.
            self.session.end(exception=sys.exc_info())

            # Make sure we unhook and disable our keypress listener.
            if self.shortcuts:
                shortcuts_handler.unhook(instance=self.instance, logger=self.logger)

            self.logger.info("==========================================================================================")
            self.logger.info("{session}".format(session=self.session))
            self.logger.info("==========================================================================================")

            # Ensure our logger object has all of it's handlers removed
            # manually in case of subsequent starts and handlers being
            # added again.s
            self.logger.handlers = []

            # Ensure authenticator puts the account in question
            # into the proper state when the instance is shutdown.
            Authenticator.offline(instance=self.instance)
