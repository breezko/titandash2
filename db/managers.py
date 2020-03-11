from django.db.models import Manager

from settings import VERSION

from modules.bot.core.configurations import ARTIFACT_TIER_MAP
from modules.bot.core.enumerations import State

from modules.auth.authenticator import Authenticator

from datetime import datetime

import uuid
import json
import logging


class UserManager(Manager):
    """
    User Model Manager.
    """
    def grab(self, username=None, token=None):
        """
        Grab the current user instance and update it's values.
        """
        # Maybe we're looking to just grab the current user in the system.
        # Attempt to do so if no username or token was specified.
        if not username and not token:
            _u = self.first()
            # Make sure we also update the users validation state
            # before returning the user object.
            self.all().update(state_json=json.dumps(Authenticator.get_state(username=_u.username, token=_u.token)))

            # Grab the user instance again from the database after
            # we've updated our state json.
            return self.first()

        _update_kwargs = {
            "username": username,
            "token": token,
            "state_json": json.dumps(Authenticator.get_state(username=username, token=token))
        }

        # Grab a reference of all available users (should only ever be one).
        _qs = self.all()
        # Update the existing user, or create one initially.
        _qs.update(**_update_kwargs) if _qs else self.create(**_update_kwargs)

        # Always returning the first available instance of
        # our user model. Pseudo singleton instance here.
        return self.first()

    def available(self):
        """
        Return whether or not a single user currently exists in the system yet or not.
        """
        return self.exists()

    def valid(self):
        """
        Return whether or not a user is valid by checking that oe exists, and that the account is authenticated correctly.
        """
        if self.available():
            # User is available, is their account in a valid state since
            # the last time we've accessed their account?
            return self.grab().state["valid"]

        # No user is available at all yet, user must
        # login to the system so an instance is present.
        return False


class ArtifactManager(Manager):
    """
    Artifact Model Manager.
    """
    def tier(self, tier, ignore=None):
        """
        Retrieve all artifacts of the specified tier.
        """
        if ignore is None:
            ignore = []

        # Filter out artifacts to only contain ones that
        # are of specified tier value.
        return self.filter(tier__tier=tier).exclude(name__in=ignore)

    def ensure_defaults(self):
        """
        Ensure all default artifact objects are generated and available.
        """
        # Local level import of our tier model.
        # Doing this here to avoid errors when importing managers with models.
        from db.models import Tier

        for tier, dictionary in ARTIFACT_TIER_MAP.items():
            # "tier" is now available when generating artifact instances
            # or grabbing them from the database.
            tier = Tier.objects.get_or_create(tier=tier)[0]

            for name, identifier in dictionary.items():
                # Get or create the required artifact object that will
                # be used by other pieces of functionality.
                self.get_or_create(
                    name=name,
                    tier=tier,
                    key=identifier[1]  # [1] - Artifact ID.
                )


class BotInstanceManager(Manager):
    """
    BotInstance Model Manager.
    """
    def grab(self):
        """
        Attempt to grab the existing bot instance, creating one if one does not exist.
        """
        if not self.all():
            # No bot instances are present yet at all.
            # Create one with default values.
            self.create()

        # Return the first available bot instance.
        # Although we support multiple, one should always be present.
        return self.first()

    def max_id(self):
        """
        Retrieve the max id from all available bot instances.
        """
        try:
            # Attempting to grab the max identifier from the name of all bot instances.
            # We can fallback to zero if a failure occurs.
            return max(
                [int(name.split(" ")[-1]) for name in self.filter(name__contains="Bot Instance").values_list("name", flat=True)]
            )
        # Value error may occur when the name of our instance
        # is not currently one of the templates that contains
        # a digit identifier.
        except ValueError:
            return 0

    def ensure_defaults(self):
        """
        Ensure the default bot instance is available when no other instances are present.
        """
        if not self.exists():
            # No bot instance currently present, go ahead and generate a brand
            # new one with defaults used.
            self.create()

    def running(self):
        """
        Retrieve all actively running bot instances.
        """
        return self.filter(state=State.RUNNING.value)


class ConfigurationManager(Manager):
    """
    Configuration Model Manager.
    """
    def ensure_defaults(self):
        """
        Ensure the default configuration is available when no other configurations are present.
        """
        # Import locally the tier model so we can add the
        # default owned tier to upgrade.
        from db.models import Tier

        if not self.exists():
            # No configuration is currently present, go ahead and generate a brand
            # new one with defaults used at first.
            _configuration = self.create(name="Default Configuration")
            _configuration.upgrade_owned_tier.add(Tier.objects.get(tier="S"))
            _configuration.save()


class GlobalConfigurationManager(Manager):
    """
    GlobalConfiguration Model Manager.
    """
    def grab(self):
        """
        Attempt to grab the existing global configuration instance, creating one if one does not exist.
        """
        if not self.all():
            # No global configuration instance is present
            # yet at all, create one with default values.
            self.create()

        # Return the first available global configuration instance.
        return self.first()


class ArtifactStatisticsManager(Manager):
    """
    ArtifactStatistics Model Manager.
    """
    def grab(self, instance):
        """
        Attempt to grab the existing artifact statistics for a specific instance, generating a new one if required.
        """
        # Import the artifact owned model locally so we can generate
        # new instances when they don't yet exist.
        from db.models import Tier, Artifact, ArtifactOwned

        if not self.filter(instance=instance):
            # No artifact statistics are available yet for the specified
            # instance, generate a new one with all artifacts unowned by default.
            _statistics = self.create(instance=instance)

            for tier, dictionary in ARTIFACT_TIER_MAP.items():
                # "tier" is now available when generating artifact instances
                # or grabbing them from the database.
                tier = Tier.objects.get_or_create(tier=tier)[0]

                for name, identifier in dictionary.items():
                    # Name and identifier can be also be used to
                    # generate artifact instance.
                    if name not in _statistics.artifacts.all().values_list("artifact__name", flat=True):
                        # Get or create the required artifact object that will
                        # be added to the statistics instance being created.
                        artifact = Artifact.objects.get_or_create(
                            name=name,
                            tier=tier,
                            key=identifier[1]
                        )[0]

                        _statistics.artifacts.add(ArtifactOwned.objects.create(
                            instance=instance,
                            artifact=artifact
                        ))

        # Retrieve the artifact statistics for the specified instance.
        # If one didn't exist, it was created above.
        return self.get(instance=instance)


class SessionManager(Manager):
    """
    Session Model Manager.
    """
    def generate(self, instance, configuration, logger):
        """
        Generate a brand new session instance for the specified instance.
        """
        # Local level import of the log model, for use
        # with the foreign key fields for session logs.
        from db.models import Log

        _uuid = uuid.uuid4().hex
        _logs = None

        # We need to make sure we look through our logger
        # for the file handler associated, making sure we
        # attach it to our session instance.
        for _handle in logger.handlers:
            # Only looking for the proper file handler.
            if isinstance(_handle, logging.FileHandler):
                _logs = _handle.baseFilename
                # Break early since we now have the log filename needed.
                break

        # Generate the session instance with the variable
        # specified and derived.
        return self.create(
            instance=instance,
            uuid=_uuid,
            version=VERSION,
            started=datetime.now(),
            log=Log.objects.create(log=_logs),
            configuration=configuration,
        )


class StatisticsManager(Manager):
    """
    Statistics Model Manager.
    """
    def grab(self, instance):
        """
        Attempt to grab the existing statistics instance for a specific instance, generating a new one if required.
        """
        # Import the game statistics and bot statistics model locally
        # so we can generate new instances when needed.
        from db.models import ArtifactStatistics, SessionStatistics, PrestigeStatistics, GameStatistics, BotStatistics

        if not self.filter(instance=instance):
            # No statistic instances are available yet for the specified
            # instance, generate a new one with default statistics fields.
            _session_statistics = SessionStatistics.objects.grab(instance=instance)
            _artifact_statistics = ArtifactStatistics.objects.grab(instance=instance)
            _prestige_statistics = PrestigeStatistics.objects.grab(instance=instance)
            _game_statistics = GameStatistics.objects.create()
            _bot_statistics = BotStatistics.objects.create()

            # Generate the new generic statistics object with our
            # newly created statistic objects.
            return self.create(
                instance=instance,
                session_statistics=_session_statistics,
                artifact_statistics=_artifact_statistics,
                prestige_statistics=_prestige_statistics,
                game_statistics=_game_statistics,
                bot_statistics=_bot_statistics
            )

        # Retrieve the statistics for the specified instance.
        # If one didn't exist, it was created above.
        return self.get(instance=instance)


class SessionStatisticsManager(Manager):
    """
    SessionStatistics Model Manager.
    """
    def grab(self, instance):
        """
        Attempt to grab the existing session statistics instance for the specific instance, generating a new one if required.
        """
        if not self.filter(instance=instance):
            # No session statistics instances are available yet for the specified
            # instance, generate a new one with default fields.
            return self.create(instance=instance)

        # Retrieve the session statistics for the specified instance.
        # If one didn't exist, it was created above.
        return self.get(instance=instance)


class PrestigeStatisticsManager(Manager):
    """
    PrestigeStatistics Model Manager.
    """
    def grab(self, instance):
        """
        Attempt to grab the existing prestige statistics instance for specific instance, generating a new one if required.
        """
        if not self.filter(instance=instance):
            # No prestige statistics instances are available yet for the specified
            # instance, generate a new one with default fields.
            return self.create(instance=instance)

        # Retrieve the prestige statistics for the specified instance.
        # If one didn't exist, it was created above.
        return self.get(instance=instance)
