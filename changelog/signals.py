import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.dispatch import receiver

from changelog.models import ChangeLog


logger = logging.getLogger(__name__)

TRACKED_MODELS_SETTING = 'CHANGELOG_TRACKED_FIELDS'
__models = None


def _get_models():
    global __models
    if __models is None:
        if not hasattr(settings, TRACKED_MODELS_SETTING):
            logger.warning(
                "Setting `{}` not found. No changes will be tracked".format(
                    TRACKED_MODELS_SETTING
                )
            )

        models = getattr(settings, TRACKED_MODELS_SETTING, {})

        __models = {}
        for model, fields in models.iteritems():
            app_label, model_name = model.split('.')
            model = ContentType.objects.filter(
                app_label=app_label,
                model=model_name.lower(),
            ).get().model_class()

            __models[model] = tuple(fields)

    return __models


def _get_field_values(instance):
    return {
        field: getattr(instance, field)
        for field
        in _get_models().get(instance.__class__, tuple())
    }


@receiver(signals.post_init, dispatch_uid='changelog.set_initial_values')
def set_initial_values(sender, instance, **kwargs):
    models = _get_models()
    if sender not in models:
        return

    instance.__changelog_initial_values = _get_field_values(instance)
    logger.debug(
        "Set initial values for tracked fields: {}".format(repr(instance))
    )


@receiver(signals.post_save, dispatch_uid='changelone.create_log')
def create_log(sender, instance, **kwargs):
    models = _get_models()
    if sender not in models:
        return

    changes = {}
    current_fields = _get_field_values(instance)
    for field, value in current_fields.iteritems():
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
