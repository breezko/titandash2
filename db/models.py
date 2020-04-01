from settings import DATETIME_FORMAT, MAX_STAGE, RELATIVE_ARTIFACT_IMAGE_DIR

from django.utils.text import slugify
from django.db.models import (
    Avg, Model, ForeignKey, CharField, TextField, BooleanField, NullBooleanField,
    PositiveIntegerField, DateTimeField, DecimalField, DurationField, ManyToManyField, CASCADE
)

from db.managers import (
    ApplicationStateManager, UserManager, ArtifactManager, BotInstanceManager, ConfigurationManager,
    GlobalConfigurationManager, ArtifactStatisticsManager, SessionManager, StatisticsManager, SessionStatisticsManager,
    PrestigeStatisticsManager
)
from db.utilities import import_model_kwargs, generate_url
from db.mixins import ExportModelMixin

from modules.bot.core.utilities import convert_to_number, format_string
from modules.bot.core.decorators import BotProperty
from modules.bot.core.exceptions import TerminationEncountered, FailsafeException
from modules.bot.core.enumerations import Duration, Level, State, SkillLevel, Perk

from datetime import datetime, timedelta
from decimal import Decimal

import json
import eel


class ApplicationState(Model):
    """
    ApplicationState Database Model.
    """
    objects = ApplicationStateManager()

    state = BooleanField(max_length=255, default=False)


class User(Model):
    """
    User Database Model.
    """
    objects = UserManager()

    username = CharField(max_length=255)
    token = CharField(max_length=255)

    # Create a char field that can store the users current
    # state json value. We can use a property to convert
    # from a string to proper dictionary,
    state_json = CharField(max_length=255)

    def __str__(self):
        return "{username} ({valid})".format(username=self.username, valid=self.state["valid"])

    def __repr__(self):
        return "<User: {user}>".format(user=self)

    @property
    def state(self):
        """
        Return a dictionary containing the state_json information present on the instance.
        """
        return json.loads(s=self.state_json)

    @property
    def json(self):
        """
        User as JSON.
        """
        return {
            "username": self.username,
            "token": self.token,
            "state": self.state
        }


class Tier(Model, ExportModelMixin):
    """
    Tier Database Model.
    """
    tier = CharField(max_length=255)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Tier: {tier}>".format(tier=self)

    @staticmethod
    def import_model_kwargs(export_string, compression_keys=None):
        """
        Not currently using model kwargs importer within tier's.
        """
        pass

    @staticmethod
    def import_model(export_kwargs):
        """
        Not currently using model importer within tier's.
        """
        pass

    def export_key(self):
        """
        Export key used when tier is encountered during model export.
        """
        return self.tier

    @property
    def name(self):
        """
        Return a name representation of the tier instance.
        """
        return "Tier {tier}".format(tier=self.tier)

    def json(self):
        """
        Tier as JSON.
        """
        return {
            "pk": self.pk,
            "tier": self.tier,
            "name": self.name
        }


class Artifact(Model, ExportModelMixin):
    """
    Artifact Database Model.
    """
    objects = ArtifactManager()

    name = CharField(max_length=255)
    tier = ForeignKey(to="Tier", on_delete=CASCADE)
    key = PositiveIntegerField()

    def __str__(self):
        return "{name} ({key}) - [{tier}]".format(
            name=self.name,
            key=self.key,
            tier=self.tier
        )

    def __repr__(self):
        return "<Artifact: {artifact}>".format(artifact=self)

    @staticmethod
    def import_model_kwargs(export_string, compression_keys=None):
        """
        Not currently using model kwargs importer within artifacts.
        """
        pass

    @staticmethod
    def import_model(export_kwargs):
        """
        Not currently using model importer within artifacts.
        """
        pass

    def export_key(self):
        """
        Export key used when artifact is encountered during model export.
        """
        return self.key

    @property
    def image(self):
        """
        Return the name of the image that's used by this artifact.
        """
        # We need to remove any apostrophes that are present in the
        # artifact name, since image paths do not support these characters.
        return "{path}/{name}.png".format(path=RELATIVE_ARTIFACT_IMAGE_DIR, name=self.name.replace("'", ""))

    def json(self):
        """
        Artifact as JSON.
        """
        return {
            "name": self.name,
            "tier": self.tier.json(),
            "key": self.key,
            "image": self.image
        }


class BotInstance(Model):
    """
    BotInstance Database Model.
    """
    # When resetting a bot instance, some fields should be left as is without explicitly
    # changing any of the values. We can ignore those here.
    RESET_IGNORE_FIELDS = [
        "name",                    # Ignore name because it shouldn't be reset through resets.
        "state",                   # Ignore state because it should persist.
        "next_raid_attack_reset",  # Ignore raid attack reset because it should persist.
        "id",
        "pk",
        "prestige",
        "queuedfunction",
        "artifactowned",
        "artifactstatistics",
        "session_instance",
        "statistics"
    ]

    objects = BotInstanceManager()

    # Generic Variables.
    name = CharField(max_length=255, blank=True, null=True)
    state = CharField(max_length=255, choices=State.choices(), default=State.STOPPED.value)
    session = ForeignKey(to="Session", blank=True, null=True, on_delete=CASCADE)
    started = DateTimeField(blank=True, null=True)
    function = CharField(max_length=255, blank=True, null=True)
    # Last Prestige Information.
    last_prestige = ForeignKey(to="Prestige", blank=True, null=True, on_delete=CASCADE)
    # Raid Attack Reset Data.
    # -----------------------
    # This field acts slightly differently compared to the other bot instance
    # attributes, value will persist throughout session start and stop.
    next_raid_attack_reset = DateTimeField(blank=True, null=True)
    # Break Variables.
    next_break = DateTimeField(blank=True, null=True)
    break_resume = DateTimeField(blank=True, null=True)
    # Bot Variables.
    configuration = ForeignKey(to="Configuration", blank=True, null=True, on_delete=CASCADE)
    window_json = TextField(blank=True, null=True)
    shortcuts = NullBooleanField(blank=True, null=True)
    log = ForeignKey(to="Log", blank=True, null=True, on_delete=CASCADE)
    stage = PositiveIntegerField(blank=True, null=True)
    newest_hero = CharField(max_length=255, blank=True, null=True)
    # Calculation Type Variables.
    next_fairy_tap = DateTimeField(blank=True, null=True)
    next_minigames_tap = DateTimeField(blank=True, null=True)
    next_master_level = DateTimeField(blank=True, null=True)
    next_heroes_level = DateTimeField(blank=True, null=True)
    next_skills_level = DateTimeField(blank=True, null=True)
    next_skills_activation = DateTimeField(blank=True, null=True)
    next_miscellaneous_actions = DateTimeField(blank=True, null=True)
    next_headgear_swap = DateTimeField(blank=True, null=True)
    next_perk_check = DateTimeField(blank=True, null=True)
    next_prestige = DateTimeField(blank=True, null=True)
    next_randomized_prestige = DateTimeField(blank=True, null=True)
    next_statistics_update = DateTimeField(blank=True, null=True)
    next_daily_achievement_check = DateTimeField(blank=True, null=True)
    next_milestone_check = DateTimeField(blank=True, null=True)
    next_raid_notifications = DateTimeField(blank=True, null=True)
    next_heavenly_strike = DateTimeField(blank=True, null=True)
    next_deadly_strike = DateTimeField(blank=True, null=True)
    next_hand_of_midas = DateTimeField(blank=True, null=True)
    next_fire_sword = DateTimeField(blank=True, null=True)
    next_war_cry = DateTimeField(blank=True, null=True)
    next_shadow_clone = DateTimeField(blank=True, null=True)
    # Next Artifact Upgrade Variables.
    next_artifact_upgrade = CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{name} [{state}]".format(
            name=self.name,
            state=self.state
        )

    def __repr__(self):
        return "<BotInstance: {bot_instance}>".format(bot_instance=self)

    def slug(self):
        """
        Slugify the current bot instance.
        """
        return slugify(value="{name}_{pk}".format(name=self.name, pk=self.pk))

    def save(self, *args, **kwargs):
        """
        Perform additional save operations when a bot instance is saved.
        """
        if not self.name:
            # No name has been configured for the bot instance, we can generate
            # one automatically using a derived template name.
            self.name = "Bot Instance {max_id}".format(max_id=BotInstance.objects.max_id() + 1)

        # Perform super so that our database instance is completely
        # up to date and saved.
        super(BotInstance, self).save(*args, **kwargs)

        # Whenever a bot instance is saved, send a signal to our frontend
        # that will handle updating our dashboard to reflect the instances
        # current state.
        eel.base_instance_updated(self.pk, self.json())

    @property
    def window(self):
        """
        Load the window json into a python dictionary.
        """
        return json.loads(self.window_json) if self.window_json else {}

    @property
    def artifacts(self):
        """
        Retrieve all artifacts and their owned state associated with this bot instance.
        """
        return ArtifactStatistics.objects.grab(instance=self)

    @property
    def prestiges(self):
        """
        Retrieve all prestige instances associated with this bot instance.
        """
        return PrestigeStatistics.objects.grab(instance=self)

    @property
    def sessions(self):
        """
        Retrieve all session instances associated with this bot instance.
        """
        return SessionStatistics.objects.grab(instance=self)

    def is_stopped(self):
        """
        Refresh and check whether or not current state of this instance is in a stopped state.
        """
        # Perform a refresh in the database.
        # Making sure the state value is up-to date.
        self.refresh_from_db()

        # Return whether or not our state is in the correct
        # "stopped" state.
        return self.state == State.STOPPED.value

    def _diff_max_stage(self, percent=False):
        """
        Attempt to retrieve the current difference from the users maximum stage, and current stage.
        """
        if not self.stage:
            # Just return early if no current stage is
            # even currently available.
            return None

        # Grabbing the current highest stage from our instances
        # associated game statistics most recent value.
        _highest_stage = Statistics.objects.grab(instance=self).game_statistics.highest_stage()

        # Maybe no highest stage is actually available yet, we can
        # also just return early with none.
        if not _highest_stage:
            return None

        # Percentage is disabled, just return the difference
        # between our maximum stage, and highest stage.
        if not percent:
            return int(_highest_stage) - self.stage

        # Maybe our maximum stage is actually currently the same
        # as our current stage, we should return "100%" explicitly
        # to avoid any issues with the percentage number.
        if _highest_stage == self.stage:
            return "100%"

        # Otherwise, calculate and return the current percent from
        # the highest stage available.
        return "{:.2%}".format(float(self.stage) / _highest_stage)

    def json(self):
        """
        BotInstance as JSON.
        """
        return {
            "pk": self.pk,
            "name": self.name,
            "state": self.state,
            "shortcuts": self.shortcuts,
            "session": self.session.json() if self.session else None,
            "configuration": self.configuration.json() if self.configuration else None,
            "window": self.window if self.window_json else None,
            "started": {
                "datetime": self.started or None,
                "formatted": self.started.strftime(format=DATETIME_FORMAT) if self.started else None
            },
            "function": self.function,
            "last_prestige": self.last_prestige.json() if self.last_prestige else None,
            "log": self.log.json() if self.log else None,
            "stage": {
                "stage": self.stage,
                "diff": self._diff_max_stage(),
                "percent": self._diff_max_stage(percent=True)
            },
            "newest_hero": self.newest_hero or None,
            "next_artifact_upgrade": Artifact.objects.get(name=self.next_artifact_upgrade).json() if self.next_artifact_upgrade else None,
            "next_fairy_tap": {
                "datetime": self.next_fairy_tap or None,
                "formatted": self.next_fairy_tap.strftime(format=DATETIME_FORMAT) if self.next_fairy_tap else None
            },
            "next_minigames_tap": {
                "datetime": self.next_minigames_tap or None,
                "formatted": self.next_minigames_tap.strftime(format=DATETIME_FORMAT) if self.next_minigames_tap else None
            },
            "next_master_level": {
                "datetime": self.next_master_level or None,
                "formatted": self.next_master_level.strftime(format=DATETIME_FORMAT) if self.next_master_level else None
            },
            "next_heroes_level": {
                "datetime": self.next_heroes_level or None,
                "formatted": self.next_heroes_level.strftime(format=DATETIME_FORMAT) if self.next_heroes_level else None
            },
            "next_skills_level": {
                "datetime": self.next_skills_level or None,
                "formatted": self.next_skills_level.strftime(format=DATETIME_FORMAT) if self.next_skills_level else None
            },
            "next_skills_activation": {
                "datetime": self.next_skills_activation or None,
                "formatted": self.next_skills_activation.strftime(format=DATETIME_FORMAT) if self.next_skills_activation else None
            },
            "next_miscellaneous_actions": {
                "datetime": self.next_miscellaneous_actions or None,
                "formatted": self.next_miscellaneous_actions.strftime(format=DATETIME_FORMAT) if self.next_miscellaneous_actions else None
            },
            "next_headgear_swap": {
                "datetime": self.next_headgear_swap or None,
                "formatted": self.next_headgear_swap.strftime(format=DATETIME_FORMAT) if self.next_headgear_swap else None
            },
            "next_perk_check": {
                "datetime": self.next_perk_check or None,
                "formatted": self.next_perk_check.strftime(format=DATETIME_FORMAT) if self.next_perk_check else None
            },
            "next_prestige": {
                "datetime": self.next_prestige or None,
                "formatted": self.next_prestige.strftime(format=DATETIME_FORMAT) if self.next_prestige else None
            },
            "next_randomized_prestige": {
                "datetime": self.next_randomized_prestige or None,
                "formatted": self.next_randomized_prestige.strftime(format=DATETIME_FORMAT) if self.next_randomized_prestige else None
            },
            "next_statistics_update": {
                "datetime": self.next_statistics_update or None,
                "formatted": self.next_statistics_update.strftime(format=DATETIME_FORMAT) if self.next_statistics_update else None
            },
            "next_daily_achievement_check": {
                "datetime": self.next_daily_achievement_check or None,
                "formatted": self.next_daily_achievement_check.strftime(format=DATETIME_FORMAT) if self.next_daily_achievement_check else None
            },
            "next_milestone_check": {
                "datetime": self.next_milestone_check or None,
                "formatted": self.next_milestone_check.strftime(format=DATETIME_FORMAT) if self.next_milestone_check else None
            },
            "next_raid_notifications": {
                "datetime": self.next_raid_notifications or None,
                "formatted": self.next_raid_notifications.strftime(format=DATETIME_FORMAT) if self.next_raid_notifications else None
            },
            "next_raid_attack_reset": {
                "datetime": self.next_raid_attack_reset or None,
                "formatted": self.next_raid_attack_reset.strftime(format=DATETIME_FORMAT) if self.next_raid_attack_reset else None
            },
            "next_heavenly_strike": {
                "datetime": self.next_heavenly_strike or None,
                "formatted": self.next_heavenly_strike.strftime(format=DATETIME_FORMAT) if self.next_heavenly_strike else None
            },
            "next_deadly_strike": {
                "datetime": self.next_deadly_strike or None,
                "formatted": self.next_deadly_strike.strftime(format=DATETIME_FORMAT) if self.next_deadly_strike else None
            },
            "next_hand_of_midas": {
                "datetime": self.next_hand_of_midas or None,
                "formatted": self.next_hand_of_midas.strftime(format=DATETIME_FORMAT) if self.next_hand_of_midas else None
            },
            "next_fire_sword": {
                "datetime": self.next_fire_sword or None,
                "formatted": self.next_fire_sword.strftime(format=DATETIME_FORMAT) if self.next_fire_sword else None
            },
            "next_war_cry": {
                "datetime": self.next_war_cry or None,
                "formatted": self.next_war_cry.strftime(format=DATETIME_FORMAT) if self.next_war_cry else None
            },
            "next_shadow_clone": {
                "datetime": self.next_shadow_clone or None,
                "formatted": self.next_shadow_clone.strftime(format=DATETIME_FORMAT) if self.next_shadow_clone else None
            },
            "next_break": {
                "datetime": self.next_break or None,
                "formatted": self.next_break.strftime(format=DATETIME_FORMAT) if self.next_break else None
            },
            "break_resume": {
                "datetime": self.break_resume or None,
                "formatted": self.break_resume.strftime(format=DATETIME_FORMAT) if self.break_resume else None
            }
        }

    def reset(self):
        """
        Reset all bot instance variables to their default none values.
        """
        # Grabbing all fields present on the bot instance that don't begin with an
        # underscore and aren't present in the specified ignorable list.
        for _field in [field.name for field in self._meta.get_fields() if not field.name.startswith("_") and field.name not in self.RESET_IGNORE_FIELDS]:
            # Dynamically assign our none value to the fields
            # grabbed through the for loop.
            setattr(self, _field, None)

        # Additionally, when a bot instance is reset, we should also
        # flush out the current set of queued functions.
        for queued in QueuedFunction.objects.filter(instance=self):
            # Just calling remove to delete and remove from the frontend.
            queued.remove()

    def start(self, session):
        """
        Start the bot instance, setting our session and log values.
        """
        self.state = State.RUNNING.value
        self.session = session
        self.log = session.log
        self.started = datetime.now()

        # Ensure we perform a save directly on the instance, ensuring
        # that our values are properly saved and signals are sent.
        self.save()

        # Send out some signals to the eel frontend
        # when a bot instance has been successfully started.
        eel.base_generate_toast("Start Instance", "<em>{name}</em> has been started successfully.".format(name=self.name), "success")
        eel.base_instance_started(self.pk)

    def pause(self):
        """
        Pause the bot instance, setting our state value as required.
        """
        self.state = State.PAUSED.value

        # Ensure we perform a save directly on the instance, ensuring
        # that our values are properly saved and signals are sent.
        self.save()

        # Send out some signals to the eel frontend
        # when a bot instance has been successfully paused.
        eel.base_generate_toast("Pause Instance", "<em>{name}</em> has been paused successfully.".format(name=self.name), "success")
        eel.base_instance_paused(self.pk)

    def resume(self):
        """
        Resume the bot instance, setting our state value as required.
        """
        self.state = State.RUNNING.value

        # Ensure we perform a save directly on the instance, ensuring
        # that our values are properly saved and signals are sent.
        self.save()

        # Send out some signals to the eel frontend
        # when a bot instance has been successfully resumed.
        eel.base_generate_toast("Resume Instance", "<em>{name}</em> has been resumed successfully.".format(name=self.name), "success")
        eel.base_instance_resumed(self.pk)

    def stop(self, exception=None, signal=True):
        """
        Stop the bot instance, setting our instance variables to none as required.
        """
        self.state = State.STOPPED.value

        # Reset all variables present on the bot instance to their default
        # state of none.
        self.reset()
        # Ensure we perform a save directly on the instance, ensuring
        # that our values are properly saved and signals are sent.
        self.save()

        # Only generating and sending our websocket signal
        # if the boolean above is set to true.
        if signal:
            _timeout = None  # Use default timeout.
            _klass = "success"
            _sender = "Stop Instance"
            _message = "<em>{name}</em> has been stopped successfully.".format(name=self.name)

            if exception and exception[0] is not None:
                # Only dealing with signal sending when an exception is available
                # and it has proper values present.
                _timeout = 10000

                if exception[0] == FailsafeException:
                    # Failsafe has been triggered by the user, display a warning message
                    # about this one because it isn't as important or critical.
                    _klass = "warning"
                    _sender = "Stop Instance (Failsafe)"
                    _message = "<em>{name}</em> encountered a <strong>fail-safe</strong> exception and has been stopped.".format(
                        name=self.name
                    )
                # An exception has been included, meaning the instance is being stopped
                # from within a running instance.
                elif exception[0] != TerminationEncountered:
                    # The exception is not a "manually" encountered one, so we should provide
                    # a danger toast with some exception information included.
                    _klass = "danger"
                    _sender = "Stop Instance (Exception)"
                    _message = "<em>{name}</em> encountered an exception and has been stopped. (<strong>{type}</strong> - {exception}).".format(
                        name=self.name,
                        type=exception[0].__name__,
                        exception=str(exception[1]).replace("'", '"')
                    )

            # Send out some signals to the eel frontend
            # when a bot instance has been successfully stopped.
            eel.base_generate_toast(_sender, _message, _klass, _timeout)
            eel.base_instance_stopped(self.pk)


class Configuration(Model, ExportModelMixin):
    """
    Configuration Database Model.
    """
    # Create a dictionary of all compression keys used by configurations.
    # These can be used to properly import and export configuration
    # instances directly into the dashboard with simple formatted strings.
    COMPRESSION_KEYS = {
        "name": 0,
        "post_action_min_wait": 1,
        "post_action_max_wait": 2,
        "enable_eggs": 3,
        "enable_tournaments": 5,
        "enable_breaks": 6,
        "breaks_jitter": 7,
        "breaks_minutes_required": 8,
        "breaks_minutes_min": 9,
        "breaks_minutes_max": 10,
        "enable_daily_achievements": 11,
        "daily_achievements_check_on_start": 12,
        "daily_achievements_check_every_x_hours": 13,
        "enable_milestones": 14,
        "milestones_check_on_start": 15,
        "milestones_check_every_x_hours": 16,
        "enable_raid_notifications": 17,
        "raid_notifications_check_on_start": 18,
        "raid_notifications_check_every_x_hours": 19,
        "enable_master": 20,
        "master_level_intensity": 21,
        "enable_heroes": 22,
        "hero_level_intensity": 23,
        "activate_skills_on_start": 24,
        "interval_heavenly_strike": 25,
        "interval_deadly_strike": 26,
        "interval_hand_of_midas": 27,
        "interval_fire_sword": 28,
        "interval_war_cry": 29,
        "interval_shadow_clone": 30,
        "skill_level_intensity": 31,
        "enable_auto_prestige": 32,
        "prestige_x_minutes": 33,
        "prestige_at_stage": 34,
        "prestige_at_max_stage": 35,
        "prestige_at_max_stage_percent": 36,
        "enable_artifact_upgrade": 37,
        "enable_artifact_discover_enchant": 38,
        "upgrade_owned_tier": 39,
        "shuffle_artifacts": 40,
        "ignore_artifacts": 41,
        "upgrade_artifacts": 42,
        "enable_statistics": 43,
        "update_statistics_on_start": 44,
        "update_statistics_every_x_minutes": 45,
        "master_level_only_once": 46,
        "enable_prestige_threshold_randomization": 47,
        "prestige_random_min_time": 48,
        "prestige_random_max_time": 49,
        "enable_minigames": 50,
        "enable_coordinated_offensive": 51,
        "enable_astral_awakening": 52,
        "enable_heart_of_midas": 53,
        "enable_flash_zip": 54,
        "enable_forbidden_contract": 55,
        "master_level_every_x_seconds": 56,
        "hero_level_every_x_seconds": 57,
        "enable_level_skills": 58,
        "level_skills_every_x_seconds": 59,
        "level_heavenly_strike_cap": 60,
        "level_deadly_strike_cap": 61,
        "level_hand_of_midas_cap": 62,
        "level_fire_sword_cap": 63,
        "level_war_cry_cap": 64,
        "level_shadow_clone_cap": 65,
        "enable_activate_skills": 66,
        "master_level_on_start": 67,
        "hero_level_on_start": 68,
        "level_skills_on_start": 69,
        "activate_skills_every_x_seconds": 70,
        "repeat_minigames": 72,
        "enable_perk_usage": 73,
        "enable_perk_diamond_purchase": 74,
        "enable_perk_only_tournament": 75,
        "use_perks_every_x_hours": 76,
        "use_perks_on_prestige": 77,
        "enable_power_of_swiping": 78,
        "enable_adrenaline_rush": 79,
        "enable_make_it_rain": 80,
        "enable_mana_potion": 81,
        "enable_doom": 82,
        "enable_mega_boost": 83,
        "enable_clan_crate": 84,
        "use_perks_on_start": 85,
        "enable_headgear_swap": 86,
        "headgear_swap_every_x_seconds": 87,
        "headgear_swap_on_start": 88,
        "log_enable": 89,
        "log_level": 90,
        "miscellaneous_actions_every_x_seconds": 91,
        "fairy_tap_every_x_seconds": 92,
        "minigames_every_x_seconds": 93,
    }

    # Create a dictionary of help texts that are associated with each field.
    # We do not need to apply these directly to the fields defined below, but
    # should include them when building out configuration forms.
    HELP_TEXT = {
        "name": "Specify a name for this configuration.",
        "post_action_min_wait": "Determine the minimum amount of seconds to wait after an in game function is finished executing.",
        "post_action_max_wait": "Determine the maximum amount of seconds to wait after an in game function is finished executing.",
        "fairy_tap_every_x_seconds": "Specify the amount of seconds between each fairy tapping process.",
        "enable_eggs": "Enable the ability to collect and hatch eggs in game.",
        "enable_tournaments": "Enable the ability to enter and participate in tournaments.",
        "miscellaneous_actions_every_x_seconds": "Specify how often miscellaneous actions should be executed in game.",
        "enable_breaks": "Enable the ability to take breaks in game.",
        "breaks_jitter": "Specify a jitter amount so that breaks take place at different intervals.",
        "breaks_minutes_required": "How many minutes of concurrent playtime is required before a break takes place.",
        "breaks_minutes_min": "Minimum amount of minutes to break for.",
        "breaks_minutes_max": "Maximum amount of minutes to break for.",
        "enable_daily_achievements": "Enable the ability to check and collect daily achievements in game.",
        "daily_achievements_check_on_start": "Should daily achievements be checked for completion when a session is started.",
        "daily_achievements_check_every_x_hours": "Determine how many hours between each daily achievement check.",
        "enable_milestones": "Enable the ability to check and collect milestones in game.",
        "milestones_check_on_start": "Should milestones be checked for completion when a session is started.",
        "milestones_check_every_x_hours": "Determine how many hours between each milestone check.",
        "enable_raid_notifications": "Should notifications be sent to when a clan raid starts or attacks are ready.",
        "raid_notifications_check_on_start": "Should a raid notifications check take place when a session is started.",
        "raid_notifications_check_every_x_minutes": "Determine how many minutes between each raid notifications check.",
        "enable_master": "Enable the ability to level the sword master in game.",
        "master_level_intensity": "Determine the amount of clicks performed whenever the sword master is levelled.",
        "enable_heroes": "Enable the ability level heroes in game.",
        "hero_level_intensity": "Determine the amount of clicks performed on each hero when they are levelled.",
        "activate_skills_on_start": "Should skills be activated once when a session is started.",
        "interval_heavenly_strike": "How many seconds between each activation of the heavenly strike skill.",
        "interval_deadly_strike": "How many seconds between each activation of the deadly strike skill.",
        "interval_hand_of_midas": "How many seconds between each activation of the hand of midas skill.",
        "interval_fire_sword": "How many seconds between each activation of the fire sword skill.",
        "interval_war_cry": "How many seconds between each activation of the war cry skill.",
        "interval_shadow_clone": "How many seconds between each activation of the shadow clone skill.",
        "skill_level_intensity": "Determine the amount of clicks performed on each skill when levelled.",
        "enable_auto_prestige": "Enable the ability to automatically prestige in game.",
        "prestige_x_minutes": "Determine the amount of minutes between each auto prestige process. This can be used for farming, or as a hard limit that is used if the thresholds below aren't met within this time limit. (0 = off).",
        "prestige_at_stage": "Determine the stage needed before the prestige process is started (Once you reach/pass this stage, you will prestige). (0 = off).",
        "prestige_at_max_stage": "Should a prestige take place once your max stage has been reached? (Stats must be up to date).",
        "prestige_at_max_stage_percent": "Determine if you would like to perform an automatic prestige once a certain percent of your max stage has been reached. You may use values larger than 100 here to push your max stage. (ie: 99, 99.5, 101) (0 = off).",
        "enable_artifact_upgrade": "Enable the ability to upgrade discovered artifacts in game after a prestige has taken place.",
        "enable_artifact_discover_enchant": "Enable the ability to discover or enchant artifacts if possible after a prestige.",
        "upgrade_owned_tier": "Upgrade a specific tier (or tiers) of artifacts only.",
        "shuffle_artifacts": "Should owned artifacts be shuffled once calculated.",
        "ignore_artifacts": "Should any specific artifacts be ignored regardless of them being owned or not.",
        "upgrade_artifacts": "Should any artifacts be specifically upgraded, disabling the above settings and choosing an artifact here will only upgrade the selected artifact(s).",
        "enable_statistics": "Enable the ability to update statistics during game sessions.",
        "update_statistics_on_start": "Should statistics be updated when a session is started.",
        "update_statistics_every_x_minutes": "Determine how many minutes between each statistics update in game.",
        "master_level_only_once": "Enable the option to only level the sword master once at the beginning of a session, and once after every prestige.",
        "enable_prestige_threshold_randomization":  "Enable the ability to add additional time to a prestige once one of the thresholds below are reached. For example, if this setting is enabled and you choose to prestige every 30 minutes, the actual prestige may take place in 33 minutes depending on the settings below. Additionally, if you choose to prestige at a percent, once you reach your percentage, the bot will wait the calculated amount of time before prestiging.",
        "prestige_random_min_time": "Specify the lower floor that will be used when calculating an amount of time to wait after a prestige threshold is reached.",
        "prestige_random_max_time": "Specify the upper ceiling that will be used when calculating an amount of time to wait after a prestige threshold is reached.",
        "enable_minigames": "Enable the ability to tap on different minigames in game.",
        "minigames_every_x_seconds": "Specify the amount of seconds between each minigame tapping functionality.",
        "enable_coordinated_offensive": "Enable coordinated offensive tapping skill minigame.",
        "enable_astral_awakening": "Enable astral awakening tapping skill minigame.",
        "enable_heart_of_midas": "Enable heart of midas tapping skill minigame.",
        "enable_flash_zip": "Enable flash zip tapping skill minigame.",
        "enable_forbidden_contract": "Enable forbidden contract tapping skill minigame.",
        "master_level_every_x_seconds": "Specify the amount of seconds to wait in between each sword master level process.",
        "hero_level_every_x_seconds": "Specify the amount of seconds to wait in between each heroes level process.",
        "enable_level_skills": "Enable the ability to level skills in game.",
        "level_skills_every_x_seconds": "Specify the amount of seconds to wait in between each skills level process.",
        "level_heavenly_strike_cap": "Choose the level cap for the heavenly strike skill.",
        "level_deadly_strike_cap": "Choose the level cap for the deadly strike skill.",
        "level_hand_of_midas_cap": "Choose the level cap for the hand of midas skill.",
        "level_fire_sword_cap": "Choose the level cap for the fire sword skill.",
        "level_war_cry_cap": "Choose the level cap for the war cry skill.",
        "level_shadow_clone_cap": "Choose the level cap for the shadow clone skill.",
        "enable_activate_skills": "Enable the ability to activate skills in game.",
        "master_level_on_start": "Should the sword master be levelled once when a session is started.",
        "hero_level_on_start": "Should heroes be levelled once when a session is started.",
        "level_skills_on_start": "Should skills be levelled once when a session is started.",
        "activate_skills_every_x_seconds": "Specify the amount of seconds to wait in between each skills activation process.",
        "repeat_minigames": "Specify how many times the minigames loop should run when executed.",
        "enable_perk_usage": "Enable the ability to use and purchase perks in game.",
        "enable_perk_diamond_purchase": "Enable the ability to purchase a perk with diamonds if you don't currently have one.",
        "enable_perk_only_tournament": "Enable the ability to only check and use perks when a tournament is joined initially.",
        "use_perks_every_x_hours": "Specify the amount of hours to wait in between each perk usage process.",
        "use_perk_on_prestige": "Choose a specific perk that you would like to use or purchase (if enabled) when a prestige occurs.",
        "enable_power_of_swiping": "Enable the power of swiping perk.",
        "enable_adrenaline_rush": "Enable the adrenaline rush perk.",
        "enable_make_it_rain": "Enable the make it rain perk.",
        "enable_mana_potion": "Enable the mana potion perk.",
        "enable_doom": "Enable the doom perk.",
        "enable_mega_boost": "Enable the mega boost perk. This perk can only be collected if vip or pi-hole ads are enabled.",
        "enable_clan_crate": "Enable the clan crate perk.",
        "use_perks_on_start": "Should perks be used or purchased when a session is started.",
        "enable_headgear_swap": "Enable the ability to swap headgear in game based on the most recently parsed hero. This setting requires that you have locked the headgear you wish to use. The first one found of the newest heroes type will be equipped.",
        "headgear_swap_every_x_seconds": "Specify the amount of seconds to wait in between each headgear swap process.",
        "headgear_swap_on_start": "Should a headgear swap be initiated when a session is started.",
        "log_enable": "Should logging be enabled when a session is started.",
        "log_level": "Choose a specific logging level to use when sessions are started."
    }

    objects = ConfigurationManager()

    name = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    # Runtime Settings.
    post_action_min_wait = PositiveIntegerField(default=0)
    post_action_max_wait = PositiveIntegerField(default=1)
    # Generic Settings.
    fairy_tap_every_x_seconds = PositiveIntegerField(default=15)
    enable_eggs = BooleanField(default=True)
    enable_daily_rewards = BooleanField(default=True)
    enable_clan_crates = BooleanField(default=True)
    enable_tournaments = BooleanField(default=True)
    miscellaneous_actions_every_x_seconds = PositiveIntegerField(default=900)
    # Minigame Settings.
    enable_minigames = BooleanField(default=False)
    minigames_every_x_seconds = PositiveIntegerField(default=20)
    repeat_minigames = PositiveIntegerField(default=1)
    enable_coordinated_offensive = BooleanField(default=False)
    enable_astral_awakening = BooleanField(default=False)
    enable_heart_of_midas = BooleanField(default=False)
    enable_flash_zip = BooleanField(default=False)
    enable_forbidden_contract = BooleanField(default=False)
    # Breaks Settings.
    enable_breaks = BooleanField(default=True)
    breaks_jitter = PositiveIntegerField(default=40)
    breaks_minutes_required = PositiveIntegerField(default=180)
    breaks_minutes_min = PositiveIntegerField(default=20)
    breaks_minutes_max = PositiveIntegerField(default=60)
    # Daily Achievement Settings.
    enable_daily_achievements = BooleanField(default=True)
    daily_achievements_check_on_start = BooleanField(default=False)
    daily_achievements_check_every_x_hours = PositiveIntegerField(default=1)
    # Milestone Settings.
    enable_milestones = BooleanField(default=True)
    milestones_check_on_start = BooleanField(default=False)
    milestones_check_every_x_hours = PositiveIntegerField(default=1)
    # Raid Notification Settings.
    enable_raid_notifications = BooleanField(default=False)
    raid_notifications_check_on_start = BooleanField(default=False)
    raid_notifications_check_every_x_minutes = PositiveIntegerField(default=30)
    # Master Action Settings.
    enable_master = BooleanField(default=True)
    master_level_intensity = PositiveIntegerField(default=5)
    master_level_on_start = BooleanField(default=True)
    master_level_every_x_seconds = PositiveIntegerField(default=60)
    master_level_only_once = BooleanField(default=False)
    # Heroes Action Settings.
    enable_heroes = BooleanField(default=True)
    hero_level_intensity = PositiveIntegerField(default=3)
    hero_level_on_start = BooleanField(default=True)
    hero_level_every_x_seconds = PositiveIntegerField(default=60)
    # Skills Level Action Settings.
    enable_level_skills = BooleanField(default=True)
    level_skills_on_start = BooleanField(default=True)
    level_skills_every_x_seconds = PositiveIntegerField(default=120)
    level_heavenly_strike_cap = CharField(max_length=255, choices=SkillLevel.choices(), default=SkillLevel.MAX.value)
    level_deadly_strike_cap = CharField(max_length=255, choices=SkillLevel.choices(), default=SkillLevel.MAX.value)
    level_hand_of_midas_cap = CharField(max_length=255, choices=SkillLevel.choices(), default=SkillLevel.MAX.value)
    level_fire_sword_cap = CharField(max_length=255, choices=SkillLevel.choices(), default=SkillLevel.MAX.value)
    level_war_cry_cap = CharField(max_length=255, choices=SkillLevel.choices(), default=SkillLevel.MAX.value)
    level_shadow_clone_cap = CharField(max_length=255, choices=SkillLevel.choices(), default=SkillLevel.MAX.value)
    # Skills Activate Action Settings.
    enable_activate_skills = BooleanField(default=True)
    activate_skills_on_start = BooleanField(default=True)
    activate_skills_every_x_seconds = PositiveIntegerField(default=30)
    interval_heavenly_strike = PositiveIntegerField(default=0)
    interval_deadly_strike = PositiveIntegerField(default=20)
    interval_hand_of_midas = PositiveIntegerField(default=30)
    interval_fire_sword = PositiveIntegerField(default=40)
    interval_war_cry = PositiveIntegerField(default=50)
    interval_shadow_clone = PositiveIntegerField(default=60)
    # Headgear Swap Settings.
    enable_headgear_swap = BooleanField(default=False)
    headgear_swap_on_start = BooleanField(default=False)
    headgear_swap_every_x_seconds = PositiveIntegerField(default=300)
    # Perk Settings.
    enable_perk_usage = BooleanField(default=False)
    enable_perk_diamond_usage = BooleanField(default=False)
    enable_perk_only_tournament = BooleanField(default=False)
    use_perks_on_start = BooleanField(default=False)
    use_perks_every_x_hours = PositiveIntegerField(default=12)
    use_perk_on_prestige = CharField(max_length=255, choices=Perk.choices(), default=Perk.NO_PERK.value)
    enable_mega_boost = BooleanField(default=False)
    enable_power_of_swiping = BooleanField(default=False)
    enable_adrenaline_rush = BooleanField(default=False)
    enable_make_it_rain = BooleanField(default=False)
    enable_mana_potion = BooleanField(default=False)
    enable_doom = BooleanField(default=False)
    enable_clan_crate = BooleanField(default=False)
    # Prestige Action Settings.
    enable_auto_prestige = BooleanField(default=True)
    enable_prestige_threshold_randomization = BooleanField(default=True)
    prestige_random_min_time = PositiveIntegerField(default=2)
    prestige_random_max_time = PositiveIntegerField(default=8)
    prestige_x_minutes = PositiveIntegerField(default=45)
    prestige_at_stage = PositiveIntegerField(default=0)
    prestige_at_max_stage = BooleanField(default=False)
    prestige_at_max_stage_percent = DecimalField(default=0, decimal_places=3, max_digits=255)
    # Artifact Action Settings.
    enable_artifact_upgrade = BooleanField(default=True)
    enable_artifact_discover_enchant = BooleanField(default=True)
    shuffle_artifacts = BooleanField(default=True)
    upgrade_owned_tier = ManyToManyField(to="Tier", blank=True, related_name="upgrade_tiers")
    ignore_artifacts = ManyToManyField(to="Artifact", blank=True, related_name="ignore_artifacts")
    upgrade_artifacts = ManyToManyField(to="Artifact", blank=True, related_name="upgrade_artifacts")
    # Statistics Settings.
    enable_statistics = BooleanField(default=True)
    update_statistics_on_start = BooleanField(default=False)
    update_statistics_every_x_minutes = PositiveIntegerField(default=60)
    # Logging Settings.
    enable_logging = BooleanField(default=True)
    logging_level = CharField(max_length=255, choices=Level.choices(), default=Level.INFO.value)

    def __str__(self):
        return "{name}".format(name=self.name)

    def __repr__(self):
        return "<Configuration: {configuration}>".format(configuration=self)

    @staticmethod
    def import_model_kwargs(export_string, compression_keys=None):
        """
        Generate the import model keyword arguments for use with configuration models.
        """
        return import_model_kwargs(export_string=export_string, compression_keys=Configuration.COMPRESSION_KEYS)

    @staticmethod
    def import_model(export_kwargs):
        """
        Import a configuration model directly into the system given a set of export kwargs.
        """
        _relation_fields = [field.name for field in Configuration._meta.get_fields() if field.name not in ExportModelMixin.GENERIC_BLACKLIST and field.many_to_many or field.many_to_one]
        _relation_kwargs = {key: value for key, value in export_kwargs.items() if key in _relation_fields}

        # Remove any relational fields from the base set of
        # parameters present in the export kwargs.
        for field in _relation_fields:
            del export_kwargs[field]

        # Update the name of the imported configuration to include
        # the proper "Imported " prefix.
        export_kwargs["name"] = "Imported {name}".format(name=export_kwargs["name"])

        # Create the base configuration object with available keyword arguments.
        # Defaulting to all normal options and stripping relational information.
        _configuration = Configuration.objects.create(**export_kwargs)

        try:
            # Parse out any foreign key information and or many to many
            # data needed to fill out these fields.
            _relation_kwargs["upgrade_owned_tier"] = [tier.pk for tier in Tier.objects.filter(tier__in=_relation_kwargs["upgrade_owned_tier"])]
            _relation_kwargs["ignore_artifacts"] = [artifact.pk for artifact in Artifact.objects.filter(key__in=_relation_kwargs["ignore_artifacts"])]
            _relation_kwargs["upgrade_artifacts"] = [artifact.pk for artifact in Artifact.objects.filter(key__in=_relation_kwargs["upgrade_artifacts"])]

            for _m2m in [_configuration.upgrade_owned_tier, _configuration.ignore_artifacts, _configuration.upgrade_artifacts]:
                # Clear out the many to many relation before
                # even attempting to add any values.
                _m2m.clear()
                # Attempt to add the proper relational values
                # to the many to many field.
                _m2m.add(**_relation_kwargs[_m2m.name])

            return _configuration

        # If at any time, an exception occurs while the new configuration is having it's
        # relational fields modified, we can delete the configuration and re-raise our error.
        except Exception:
            _configuration.delete()
            # Re-raise exception to propagate up and out of import.
            raise

    def export_key(self):
        """
        Export key used when a configuration is encountered during model export.
        """
        return self.name

    @property
    def created(self):
        """
        Return the created datetime for the configuration in the proper format.
        """
        return self.created_at.strftime(format=DATETIME_FORMAT)

    @property
    def updated(self):
        """
        Return the updated datetime for the configuration in the proper format.
        """
        return self.updated_at.strftime(format=DATETIME_FORMAT)

    def form_dictionary(self):
        """
        Return a dictionary containing all information used when generating configuration instances.
        """
        return {
            "configuration": self.json(),
            "help_text": self.HELP_TEXT,
            "choices": {
                "skill_levels": SkillLevel.choices(),
                "parks": Perk.choices(),
                "levels": Level.choices(),
                "artifacts": Artifact.objects.all().values_list("pk", flat=True),
                "tiers": Tier.objects.all().values_list("pk", flat=True),
            }
        }

    def json(self):
        """
        Configuration as JSON.
        """
        return {
            "pk": self.pk,
            "url": generate_url(model=Configuration, key=self.pk),
            "name": self.name
        }

    def data(self):
        """
        Configuration as DATA.
        """
        return {
            "General": {
                "name": self.name,
                "created": self.created,
                "updated": self.updated
            },
            "Runtime": {
                "post_action_min_wait": self.post_action_min_wait,
                "post_action_max_wait": self.post_action_max_wait
            },
            "Generic": {
                "fairy_tap_every_x_seconds": self.fairy_tap_every_x_seconds,
                "enable_eggs": self.enable_eggs,
                "enable_daily_rewards": self.enable_daily_rewards,
                "enable_clan_crates": self.enable_clan_crates,
                "enable_tournaments": self.enable_tournaments
            },
            "Minigames": {
                "enable_minigames": self.enable_minigames,
                "minigames_every_x_seconds": self.minigames_every_x_seconds,
                "repeat_minigames": self.repeat_minigames,
                "enable_coordinated_offensive": self.enable_coordinated_offensive,
                "enable_astral_awakening": self.enable_astral_awakening,
                "enable_heart_of_midas": self.enable_heart_of_midas,
                "enable_flash_zip": self.enable_flash_zip,
                "enable_forbidden_contract": self.enable_forbidden_contract
            },
            "Breaks": {
                "enable_breaks": self.enable_breaks,
                "breaks_jitter": self.breaks_jitter,
                "breaks_minutes_required": self.breaks_minutes_required,
                "breaks_minutes_min": self.breaks_minutes_min,
                "breaks_minutes_max": self.breaks_minutes_max
            },
            "Daily Achievements": {
                "enable_daily_achievements": self.enable_daily_achievements,
                "daily_achievements_check_on_start": self.daily_achievements_check_on_start,
                "daily_achievements_check_every_x_hours": self.daily_achievements_check_every_x_hours
            },
            "Milestones": {
                "enable_milestones": self.enable_milestones,
                "milestones_check_on_start": self.milestones_check_on_start,
                "milestones_check_every_x_hours": self.milestones_check_every_x_hours
            },
            "Raid Notifications": {
                "enable_raid_notifications": self.enable_raid_notifications,
                "raid_notifications_check_on_start": self.raid_notifications_check_on_start,
                "raid_notifications_check_every_x_minutes": self.raid_notifications_check_every_x_minutes
            },
            "Master Action": {
                "enable_master": self.enable_master,
                "master_level_intensity": self.master_level_intensity,
                "master_level_on_start": self.master_level_on_start,
                "master_level_every_x_seconds": self.master_level_every_x_seconds,
                "master_level_only_once": self.master_level_only_once
            },
            "Heroes Action": {
                "enable_heroes": self.enable_heroes,
                "hero_level_intensity": self.hero_level_intensity,
                "hero_level_on_start": self.hero_level_on_start,
                "hero_level_every_x_seconds": self.hero_level_every_x_seconds
            },
            "Skills Level Action": {
                "enable_level_skills": self.enable_level_skills,
                "level_skills_on_start": self.level_skills_on_start,
                "level_skills_every_x_seconds": self.level_skills_every_x_seconds,
                "level_heavenly_strike_cap": self.level_heavenly_strike_cap,
                "level_deadly_strike_cap": self.level_deadly_strike_cap,
                "level_hand_of_midas_cap": self.level_hand_of_midas_cap,
                "level_fire_sword_cap": self.level_fire_sword_cap,
                "level_war_cry_cap": self.level_war_cry_cap,
                "level_shadow_clone_cap": self.level_shadow_clone_cap
            },
            "Skills Activate Action": {
                "enable_activate_skills": self.enable_activate_skills,
                "activate_skills_on_start": self.activate_skills_on_start,
                "activate_skills_every_x_seconds": self.activate_skills_every_x_seconds,
                "interval_heavenly_strike": self.interval_heavenly_strike,
                "interval_deadly_strike": self.interval_deadly_strike,
                "interval_hand_of_midas": self.interval_hand_of_midas,
                "interval_fire_sword": self.interval_fire_sword,
                "interval_war_Cry": self.interval_war_cry,
                "interval_shadow_clone": self.interval_shadow_clone
            },
            "Headgear Swap": {
                "enable_headgear_swap": self.enable_headgear_swap,
                "headgear_swap_on_start": self.headgear_swap_on_start,
                "headgear_swap_every_x_seconds": self.hero_level_every_x_seconds
            },
            "Perks": {
                "enable_perk_usage": self.enable_perk_usage,
                "enable_perk_diamond_usage": self.enable_perk_diamond_usage,
                "enable_perk_only_tournament": self.enable_perk_only_tournament,
                "use_perks_on_start": self.use_perks_on_start,
                "use_perks_every_x_hours": self.use_perks_every_x_hours,
                "use_perk_on_prestige": self.use_perk_on_prestige,
                "enable_mega_boost": self.enable_mega_boost,
                "enable_power_of_swiping": self.enable_power_of_swiping,
                "enable_adrenaline_rush": self.enable_adrenaline_rush,
                "enable_make_it_rain": self.enable_make_it_rain,
                "enable_mana_potion": self.enable_mana_potion,
                "enable_doom": self.enable_doom,
                "enable_clan_crate": self.enable_clan_crate
            },
            "Prestige": {
                "enable_auto_prestige": self.enable_auto_prestige,
                "enable_prestige_threshold_randomization": self.enable_prestige_threshold_randomization,
                "prestige_random_min_time": self.prestige_random_min_time,
                "prestige_random_max_time": self.prestige_random_max_time,
                "prestige_x_minutes": self.prestige_x_minutes,
                "prestige_at_stage": self.prestige_at_stage,
                "prestige_at_max_stage": self.prestige_at_max_stage,
                "prestige_at_max_stage_percent": self.prestige_at_max_stage_percent
            },
            "Artifacts": {
                "enable_artifact_upgrade": self.enable_artifact_upgrade,
                "enable_artifact_discover_enchant": self.enable_artifact_discover_enchant,
                "shuffle_artifacts": self.shuffle_artifacts,
                "upgrade_owned_tier": ", ".join([tier.name for tier in self.upgrade_owned_tier.all()]),
                "ignore_artifacts": ", ".join([artifact.name for artifact in self.ignore_artifacts.all()]),
                "upgrade_artifacts": ", ".join([artifact.name for artifact in self.upgrade_artifacts.all()])
            },
            "Statistics": {
                "enable_statistics": self.enable_statistics,
                "update_statistics_on_start": self.update_statistics_on_start,
                "update_statistics_every_x_minutes": self.update_statistics_every_x_minutes
            },
            "Logging": {
                "enable_logging": self.enable_logging,
                "logging_level": self.logging_level
            }
        }


class GlobalConfiguration(Model):
    """
    GlobalConfiguration Database Model.
    """
    # Create a dictionary of help texts that are associated with each field.
    # These can be included when building our global configurations forms.
    HELP_TEXT = {
        "enable_failsafe": "Enable the failsafe functionality when a bot session is running.",
        "enable_game_event": "Enable this setting whenever a timed in game event is currently running.",
        "enable_pihole": "Enable this setting if you have a pihole server setup and running to disable ads in game."
    }

    objects = GlobalConfigurationManager()

    enable_failsafe = BooleanField(default=True)
    enable_game_event = BooleanField(default=False)
    enable_pihole = BooleanField(default=False)

    def __str__(self):
        return "GlobalConfiguration {pk}".format(pk=self.pk)

    def __repr__(self):
        return "<GlobalConfiguration: {global_configuration}>".format(global_configuration=self)

    def form_dictionary(self):
        """
        Return a dictionary containing all information used when generating global configuration instances.
        """
        return {
            "global_configuration": self.json(),
            "help_text": self.HELP_TEXT
        }

    def json(self):
        """
        GlobalConfiguration as JSON.
        """
        return {
            "enable_failsafe": self.enable_failsafe,
            "enable_game_event": self.enable_game_event,
            "enable_pihole": self.enable_pihole
        }


class Prestige(Model):
    """
    Prestige Database Model.
    """
    timestamp = DateTimeField(auto_now_add=True)
    duration = DurationField(blank=True, null=True)
    stage = PositiveIntegerField(blank=True, null=True)
    artifact = ForeignKey(to="Artifact", blank=True, null=True, on_delete=CASCADE)
    instance = ForeignKey(to="BotInstance", on_delete=CASCADE)
    session = ForeignKey(to="Session", on_delete=CASCADE)

    def __str__(self):
        return "Prestige [{stage} - {duration}]".format(
            stage=self.stage,
            duration=self.duration
        )

    def __repr__(self):
        return "<Prestige: {prestige}>".format(prestige=self)

    def json(self):
        """
        Prestige as JSON.
        """
        return {
            "pk": self.pk,
            "instance": self.instance.pk,
            "timestamp": {
                "datetime": self.timestamp,
                "formatted": self.timestamp.strftime(format=DATETIME_FORMAT),
                "epoch": self.timestamp.timestamp()
            },
            "duration": {
                "formatted": self.duration or None,
                "seconds": self.duration.total_seconds() if self.duration else None
            },
            "stage": self.stage or None,
            "artifact": self.artifact.json() if self.artifact else None,
            "session": {
                "pk": self.session.pk,
                "uuid": self.session.uuid,
                "url": self.session.url
            }
        }


class QueuedFunction(Model):
    """
    QueuedFunction Database Model.
    """
    instance = ForeignKey(to="BotInstance", blank=True, null=True, on_delete=CASCADE)
    function = CharField(max_length=255)
    queued = DateTimeField()
    duration = PositiveIntegerField()
    duration_type = CharField(max_length=255, choices=Duration.choices())
    eta = DateTimeField()

    def __str__(self):
        return "Queued: {function} (Queued: {queued} - ETA: {eta})".format(
            function=self.function,
            queued=self.queued,
            eta=self.eta
        )

    def __repr__(self):
        return "<QueuedFunction: {queued_function}>".format(queued_function=self)

    def add_to_frontend(self):
        """
        Attempt to add the queued function to the frontend.
        """
        eel.base_queue_function_add(self.json())

    def remove_from_frontend(self):
        """
        Attempt to remove the queued function from the frontend if it's present in the queued function table.
        """
        eel.base_queue_function_remove(self.pk)

    def remove(self):
        """
        Remove this queued function, sending a signal to also attempt to remove the queued function from the frontend.
        """
        self.remove_from_frontend()
        self.delete()

    def save(self, *args, **kwargs):
        """
        Override base save functionality, make sure we deal with durations and custom eta.
        """
        duration = self.duration or 0
        typ = self.duration_type or Duration.SECONDS.value
        # Make sure our duration is properly coerced into an integer
        # for use with the positive integer field.
        self.duration = int(duration)
        self.duration_type = typ.lower()
        # Update the datetime that the function was "queued"
        # to be set to the current timestamp.
        self.queued = datetime.now()

        # Ensure the eta is generated successfully for our function.
        # base don the duration and duration type available.
        self.eta = datetime.now() + timedelta(**{self.duration_type: self.duration})

        _message = "Function: <strong>{function}</strong> has been queued successfully (ETA: {eta}).".format(
            function=format_string(string=self.function, lower=True),
            eta=self.eta.strftime(format=DATETIME_FORMAT)
        )
        # Generate a toast about the functions that's been queued up.
        eel.base_generate_toast("Queue Function", _message, "success")

        # Perform normal save after eta has been set.
        super(QueuedFunction, self).save(*args, **kwargs)

        # Attempt to add the function to the frontend after the
        # save method is correctly called (pk is present).
        self.add_to_frontend()

    def json(self):
        """
        QueuedFunction as JSON.
        """
        return {
            "pk": self.pk,
            "function": self.function,
            "queued": self.queued.strftime(format=DATETIME_FORMAT),
            "eta": self.eta.strftime(format=DATETIME_FORMAT),
            "duration": self.duration,
            "duration_type": self.duration_type
        }


class ArtifactOwned(Model):
    """
    ArtifactOwned Database Model.
    """
    instance = ForeignKey(to="BotInstance", on_delete=CASCADE)
    artifact = ForeignKey(to="Artifact", on_delete=CASCADE)
    owned = BooleanField(default=False)

    def __str__(self):
        return "{artifact} ({owned})".format(
            artifact=self.artifact.name,
            owned=self.owned
        )

    def __repr__(self):
        return "<ArtifactOwned: {artifact_owned}>".format(artifact_owned=self)

    def json(self):
        """
        ArtifactOwned as JSON.
        """
        return {
            "instance": self.instance.pk,
            "artifact": self.artifact.json(),
            "owned": self.owned
        }


class Log(Model):
    """
    Log Database Model.
    """
    log = CharField(max_length=255)

    def __str__(self):
        return self.log

    def __repr__(self):
        return "<Log: {log}>".format(log=self)

    def exists(self):
        """
        Determine whether or not this log file reference actually exists,
        """
        try:
            return open(self.log) is not None
        except FileNotFoundError:
            return False

    def contents(self, truncate=False, limit=3000):
        """
        Retrieve the current contents from the log file.
        """
        _dct = {
            "data": [],
            "length": 0
        }
        # Open the log file and begin appending the data from
        # the file into our dictionary.
        with open(self.log) as file:
            # Loop through each index and line in the file,
            # we need to add each line.
            for index, line in enumerate(file.readlines(), start=1):
                _dct["data"].append({
                    "index": index,
                    "line": line
                })

                if index > limit and truncate:
                    # Break early if we've limited this set of log data.
                    break

        _dct["length"] = index

        # Return the final derived dictionary of log file information.
        return _dct

    def json(self):
        """
        Log as JSON.
        """
        return {
            "pk": self.pk,
            "url": generate_url(model=Log, key=self.pk),
            "log": self.log
        }


class Session(Model):
    """
    Session Database Model.
    """
    objects = SessionManager()

    instance = ForeignKey(to="BotInstance", related_name="session_instance")
    uuid = CharField(max_length=255)
    version = CharField(max_length=255)
    started = DateTimeField()
    stopped = DateTimeField(blank=True, null=True)
    log = ForeignKey(to="Log", on_delete=CASCADE)
    configuration = ForeignKey(to="Configuration", on_delete=CASCADE)
    snapshot_json = TextField()

    def __str__(self):
        return "Session {uuid} [{version}]".format(
            uuid=self.uuid,
            version=self.version
        )

    def __repr__(self):
        return "<Session: {session}>".format(session=self)

    @property
    def url(self):
        """
        Retrieve the url that can be used to retrieve this session.
        """
        return generate_url(model=Session, key=self.pk),

    @property
    def snapshot(self):
        """
        Return a dictionary containing the snapshot_json information present on the instance.
        """
        return json.loads(self.snapshot_json)

    @property
    def duration(self):
        """
        Calculate the duration of this session based on the current started and stopped values.
        """
        if not self.stopped:
            # Session is probably still running?
            # That, or the session exited without properly
            # updating values, just use N/A.
            return "N/A"

        # Otherwise, we can just safely return the delta
        # for our two timestamp fields.
        return self.stopped - self.started

    def end(self, exception):
        """
        End the current session, setting our stopped value and saving the session.
        """
        self.instance.stop(exception=exception)
        self.stopped = datetime.now()
        self.save()

    def save(self, *args, **kwargs):
        """
        Override session save method, ensure configuration snapshot is present.
        """
        if not self.pk:
            # Only ever messing with a configuration snapshot
            # on the initial creation of the session.
            _configuration_json = self.configuration.data()

            # Ensure that any decimal values present within the configuration
            # snapshot are correctly coerced to strings instead of decimals.
            for group, _dict in _configuration_json.items():
                for key, value in _dict.items():
                    if isinstance(value, Decimal):
                        _configuration_json[group][key] = str(value)

            self.snapshot_json = json.dumps(_configuration_json)

        # Call super to ensure snapshot json is properly saved
        # on this instance.
        super(Session, self).save(*args, **kwargs)

    def json(self):
        """
        Session as JSON.
        """
        return {
            "pk": self.pk,
            "instance": self.instance.pk,
            "url": self.url,
            "uuid": self.uuid,
            "version": self.version,
            "started": {
                "datetime": self.started,
                "formatted": self.started.strftime(format=DATETIME_FORMAT),
                "epoch": self.started.timestamp()
            },
            "stopped": {
                "datetime": self.stopped or None,
                "formatted": self.stopped.strftime(format=DATETIME_FORMAT) if self.stopped else "N/A",
                "epoch": self.stopped.timestamp() if self.stopped else None
            },
            "duration": {
                "formatted": self.duration or None,
                "seconds": self.duration.total_seconds() if self.duration != "N/A" else None
            },
            "log": self.log.json(),
            "configuration": self.snapshot,
            "prestiges": [prestige.json() for prestige in Prestige.objects.filter(session=self)]
        }


class SessionStatistics(Model):
    """
    SessionStatistics Database Model.
    """
    objects = SessionStatisticsManager()

    instance = ForeignKey(to="BotInstance", on_delete=CASCADE)
    sessions = ManyToManyField(to="Session", blank=True)

    def __str__(self):
        return "SessionStatistics ({pk})".format(pk=self.pk)

    def __repr__(self):
        return "<SessionStatistics: {session_statistics}>".format(session_statistics=self)

    def json(self):
        """
        SessionStatistics as JSON.
        """
        return {
            "instance": self.instance.pk,
            "sessions": [session.json() for session in self.sessions.all()]
        }


class ArtifactStatistics(Model):
    """
    ArtifactStatistics Database Model.
    """
    objects = ArtifactStatisticsManager()

    instance = ForeignKey(to="BotInstance", on_delete=CASCADE)
    artifacts = ManyToManyField(to="ArtifactOwned", blank=True)

    def __str__(self):
        return "ArtifactStatistics ({owned}/{count})".format(
            owned=self.owned().count(),
            count=self.artifacts.all().count()
        )

    def __repr__(self):
        return "<ArtifactStatistics: {artifact_statistics}>".format(artifact_statistics=self)

    def owned(self):
        """
        Retrieve all owned artifacts for this artifact statistics instance.
        """
        return self.artifacts.filter(owned=True)

    def unowned(self):
        """
        Retrieve all unowned artifacts for this artifact statistics instance.
        """
        return self.artifacts.filter(owned=False)

    def json(self):
        """
        ArtifactStatistics as JSON.
        """
        return {
            "instance": self.instance.pk,
            "artifacts": [artifact.json() for artifact in self.artifacts.all()]
        }


class PrestigeStatistics(Model):
    """
    PrestigeStatistics Database Model.
    """
    objects = PrestigeStatisticsManager()

    instance = ForeignKey(to="BotInstance", on_delete=CASCADE)
    prestiges = ManyToManyField(to="Prestige", blank=True)

    def __str__(self):
        return "PrestigeStatistics ({pk})".format(pk=self.pk)

    def __repr__(self):
        return "<PrestigeStatistics: {prestige_statistics}>".format(prestige_statistics=self)

    def json(self):
        """
        PrestigeStatistics as JSON.
        """
        _qs = self.prestiges.all()

        return {
            "instance": self.instance.pk,
            "count": _qs.count(),
            "average_stage": _qs.aggregate(Avg("stage"))["stage__avg"],
            "average_duration": _qs.aggregate(Avg("duration"))["duration__avg"],
            "prestiges": [prestige.json() for prestige in self.prestiges.all()]
        }


class GameStatistics(Model):
    """
    GameStatistics Database Model.
    """
    highest_stage_reached = CharField(max_length=255, blank=True, null=True)
    total_pet_level = CharField(max_length=255, blank=True, null=True)
    gold_earned = CharField(max_length=255, blank=True, null=True)
    taps = CharField(max_length=255, blank=True, null=True)
    titans_killed = CharField(max_length=255, blank=True, null=True)
    bosses_killed = CharField(max_length=255, blank=True, null=True)
    critical_hits = CharField(max_length=255, blank=True, null=True)
    chestersons_killed = CharField(max_length=255, blank=True, null=True)
    prestiges = CharField(max_length=255, blank=True, null=True)
    days_since_install = CharField(max_length=255, blank=True, null=True)
    play_time = CharField(max_length=255, blank=True, null=True)
    relics_earned = CharField(max_length=255, blank=True, null=True)
    fairies_tapped = CharField(max_length=255, blank=True, null=True)
    daily_achievements = CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "GameStatistics ({pk})".format(pk=self.pk)

    def __repr__(self):
        return "<GameStatistics: {game_statistics}>".format(game_statistics=self)

    def highest_stage(self):
        """
        Retrieve the highest stage reached as a proper integer.
        """
        if not self.highest_stage_reached:
            # If not highest stage statistic is currently available
            # on the game statistics instance, return none early.
            return None

        # Otherwise, we can try to return the converted
        # highest stage value.
        return convert_to_number(value=self.highest_stage_reached)

    def average_time_played(self):
        """
        Parse out the average amount of time played per day based on the users play time and time since install.
        """
        if not self.days_since_install or not self.play_time:
            # The required statistics values are not
            # yet present for the instances statistics.
            return "N/A"

        installed = int(self.days_since_install)

        # Let's try to parse the total play time value
        # for this instances statistics to grab the amount of
        # hours played currently.
        try:
            if "d" in self.play_time:
                # A "d" is available in the play time, which means the instance
                # has played for longer than a single day.
                played = int(self.play_time.split("d")[0]) * 24
            else:
                # No "d" in the value, so we can assume the user
                # has only played for less than 24 hours.
                played = int(self.play_time.split(":")[0])

        # An unknown error could occur if any of the statistic
        # values needed are malformed. Just use base string.
        except Exception:
            return "N/A"

        # Round the number of played hours divided by the
        # total amount of hours played.
        return round(played / installed, 2)

    def max_stage_progress(self):
        """
        Return the current progress towards the maximum stage available in the game.
        """
        # Parse out the highest stage from the instances
        # current highest_stage_reached value.
        highest_stage = self.highest_stage()

        return {
            "stage": highest_stage,
            "max_stage": MAX_STAGE,
            "percent": round((highest_stage / MAX_STAGE) * 100, 2)
        }

    def time_played(self):
        """
        Return the current time played information.
        """
        return {
            "days_since_install": self.days_since_install or 0,
            "play_time": self.play_time or 0,
            "average": self.average_time_played()
        }

    def json(self):
        """
        GameStatistics as JSON.
        """
        return {
            "highest_stage_reached": self.highest_stage_reached,
            "total_pet_level": self.total_pet_level,
            "gold_earned": self.gold_earned,
            "taps": self.taps,
            "titans_killed": self.titans_killed,
            "bosses_killed": self.bosses_killed,
            "critical_hits": self.critical_hits,
            "chestersons_killed": self.chestersons_killed,
            "prestiges": self.prestiges,
            "days_since_install": self.days_since_install,
            "play_time": self.play_time,
            "relics_earned": self.relics_earned,
            "fairies_tapped": self.fairies_tapped,
            "daily_achievements": self.daily_achievements
        }


class BotStatistics(Model):
    """
    BotStatistics Database Model.
    """
    ads_collected = PositiveIntegerField(default=0)

    # Using a custom field to store json information about current bot property
    # functions and how many times they have all ben executed by an instance.
    properties_json = TextField()

    def __str__(self):
        return "BotStatistics ({pk})".format(pk=self.pk)

    def __repr__(self):
        return "<BotStatistics: {bot_statistics}>".format(bot_statistics=self)

    @property
    def properties(self):
        """
        Load the properties json data into a python dictionary.
        """
        if not self.properties_json:
            # If not json is present yet, it's probably the first
            # go through our statistics object, use empty dictionary to start.
            return {}

        return json.loads(self.properties_json)

    def set_properties(self, dct):
        """
        Set the properties json to the specified dictionary of information,.
        """
        self.properties_json = json.dumps(dct)
        self.save()

    def increment_property(self, prop):
        """
        Increment the specified property by one.
        """
        _original = self.get_properties()

        # Dynamically grabbing the property specified and incrementing the current value
        # by one. Since our bot can have functions added or removed, we need to make sure
        # we properly grab it and increment it.
        _value = _original.get(prop)

        # If the value exists and the specified property didn't
        # return a none value, we can increment properly.
        if _value is not None:
            # Dynamically set attribute.
            # Incrementing by one.
            _original[prop] = _value + 1
            # Update the properties dictionary with our
            # newly incremented value.
            self.set_properties(dct=_original)

    def get_properties(self):
        """
        Retrieve and load the property json information, updating the dictionary with missing keys if needed.
        """
        _original = self.properties
        _save = False

        # Parse out all of our functions available on the base bot class.
        # Making sure they are all present in the original dictionary of functions.
        _bot_props = BotProperty.all()

        # Parse out any of the properties that are no longer present
        # in the bot properties available at the time of retrieval.
        removed = {prop for prop in _original if prop not in [_prop["name"] for _prop in _bot_props]}

        if removed:
            # If any of our original bot properties are no longer available
            # within the derived bot properties, we need to remove them from
            # our original dictionary.
            _original = {key: value for key, value in _original.items() if key not in removed}
            _save = True

        # Parse out any of the missing properties that are not already
        # present in our properties json.
        missing = {prop["name"]: 0 for prop in _bot_props if prop["name"] not in _original}

        if missing:
            # Some properties aren't yet present in the json data for
            # our bot properties, update the original with this information.
            _original.update(missing)
            _save = True

        # We should set the properties json to our new dictionary
        # of information so that everything is up to date if the
        # structure of the properties has changed.
        if _save:
            self.set_properties(dct=_original)

        # If any values were not present before, we would have updated the value
        # above, otherwise, original values are fine to return.
        return _original

    def save(self, *args, **kwargs):
        """
        Override save method to ensure that dynamic bot properties are grabbed on creation.
        """
        if not self.pk and not self.properties:
            # If no primary key is yet available on the instance, it means
            # we are creating the instance now.
            return self.get_properties()

        super(BotStatistics, self).save(*args, **kwargs)

    def json(self):
        """
        BotStatistics as JSON.
        """
        return {
            "generic": {
                "ads_collected": self.ads_collected
            },
            "functions": self.properties
        }


class Statistics(Model):
    """
    Statistics Database Model.
    """
    objects = StatisticsManager()

    instance = ForeignKey(to="BotInstance", on_delete=CASCADE)
    session_statistics = ForeignKey(to="SessionStatistics", on_delete=CASCADE)
    artifact_statistics = ForeignKey(to="ArtifactStatistics", on_delete=CASCADE)
    prestige_statistics = ForeignKey(to="PrestigeStatistics", on_delete=CASCADE)
    game_statistics = ForeignKey(to="GameStatistics", on_delete=CASCADE)
    bot_statistics = ForeignKey(to="BotStatistics", on_delete=CASCADE)

    def __str__(self):
        return "Statistics ({pk})".format(pk=self.pk)

    def __repr__(self):
        return "<Statistics: {statistics}>".format(statistics=self)

    def json(self):
        """
        Statistics as JSON.
        """
        return {
            "instance": self.instance.pk,
            "session_statistics": self.session_statistics.json(),
            "artifact_statistics": self.artifact_statistics.json(),
            "prestige_statistics": self.prestige_statistics.json(),
            "game_statistics": self.game_statistics.json(),
            "bot_statistics": self.bot_statistics.json()
        }
