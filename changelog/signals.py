import logging

from django.db.models import signals
from django.dispatch import receiver

from changelog.models import ChangeLog
from changelog.utils import get_tracked_models


logger = logging.getLogger(__name__)

TRACKED_MODELS_SETTING = 'CHANGELOG_TRACKED_FIELDS'


def _get_field_values(instance):
    return {
        field: getattr(instance, field)
        for field
        in get_tracked_models().get(instance.__class__, tuple())
    }


@receiver(signals.post_init, dispatch_uid='changelog.set_initial_values')
def set_initial_values(sender, instance, **kwargs):
    models = get_tracked_models()
    if sender not in models:
        return

    instance.__changelog_initial_values = _get_field_values(instance)
    logger.debug(
        "Set initial values for tracked fields: {}".format(repr(instance))
    )


@receiver(signals.post_save, dispatch_uid='changelone.create_log')
def create_log(sender, instance, **kwargs):
    models = get_tracked_models()
    if sender not in models:
        return

    changes = {}
    current_fields = _get_field_values(instance)
    for field, value in current_fields.items():
        # TODO: is it possible that initial values aren't there?
        initial_value = instance.__changelog_initial_values[field]
        if initial_value != value:
            changes[field] = {
                'was': initial_value,
                'now': value,
            }

    if changes:
        log = ChangeLog.objects.create(
            instance=instance,
            fields=changes,
        )
        logger.debug("Created Log: {}".format(repr(log)))

        instance.__changelog_initial_values = current_fields
