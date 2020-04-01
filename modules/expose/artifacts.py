from db.models import BotInstance, ArtifactStatistics, Artifact

from modules.bot.core.utilities import format_string

import eel


@eel.expose
def artifacts_information(selected_instance=None):
    """
    Grab all artifacts information for a specific instance, or the default.
    """
    if selected_instance:
        # A specific instance was specified, use that instead
        # of populating an entire dictionary.
        instance = BotInstance.objects.get(pk=selected_instance)
        return {
            "pk": instance.pk,
            "name": instance.name,
            "artifacts": ArtifactStatistics.objects.grab(instance=instance).json()
        }

    dct = {"instances": []}

    # Loop through all our instances, adding each one to our
    # dictionary of information.
    for instance in BotInstance.objects.all():
        dct["instances"].append({
            "pk": instance.pk,
            "name": instance.name,
            "artifacts": ArtifactStatistics.objects.grab(instance=instance).json()
        })

    # Return our dictionary once all instances and their
    # information is available.
    return dct


@eel.expose
def artifacts_toggle(artifact, instance, owned):
    """
    Toggle the owned state to the specified value for the instances artifact.
    """
    instance = BotInstance.objects.get(pk=instance)
    statistics = ArtifactStatistics.objects.grab(instance=instance)

    # Update the actual artifact object so it's backend state
    # is successfully set to the proper value.
    statistics.artifacts.filter(artifact__key=artifact).update(owned=owned)

    message = "<em>{instance_name}</em> artifact: <em>{artifact_name}</em> has been successfully set to <strong>{owned}</strong>.".format(
        instance_name=instance.name,
        artifact_name=format_string(string=Artifact.objects.get(key=artifact).name),
        owned="owned" if owned else "un-owned"
    )

    # Send out a toast notification so the user can get
    # some feedback about their action. Using a smaller
    # timeout value to reduce notification bloat.
    eel.base_generate_toast("Toggle Owned Artifact", message, "success", 1500)
