import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from changelog.models import ChangeLog, ChangeSet


logger = logging.getLogger(__name__)


TRACKED_MODELS_SETTING = 'CHANGELOG_TRACKED_FIELDS'
__models = None


def get_tracked_models():
    """Return a dict of tracked models and fields"""
    global __models
    if __models is None:
        if not hasattr(settings, TRACKED_MODELS_SETTING):
            logger.warning(
                "Setting `{}` not found. No changes will be tracked".format(
                    TRACKED_MODELS_SETTING
                )
            )

        config = getattr(settings, TRACKED_MODELS_SETTING, {})

        __models = {}
        for model, fields in config.items():
            app_label, model_name = model.split('.')
            try:
                content_type = ContentType.objects.filter(
                    app_label=app_label,
                    model=model_name.lower(),
                ).get()
            except ContentType.DoesNotExist:
                # may happen if the tracked models' classes have no tables yet
                logger.debug(
                    'Table for `{}` not found, aborting.'.format(model)
                )
                # set to None so config loads again next time.
                __models = None
                return {}

            __models[content_type.model_class()] = tuple(fields)

    return __models


def create_sync_logs(model=None, queryset=None):
    """Iterate through instances, creating sync ``ChangeLog``s"""

    if (
        (model is None and queryset is None) or
        (model is not None and queryset is not None)
    ):
        raise TypeError("A model or queryset must be provided, but not both.")

    if model is None:
        model = queryset.model
    elif queryset is None:
        queryset = model.objects.all()

    config = get_tracked_models()

    if model not in config:
        raise ValueError(
            'Model {} is not a tracked model'.format(model.__class__.__name__)
        )

    for instance in queryset:
        diff = {}
        logged_diff = ChangeSet(instance=instance).diff

        for field in config[model]:
            value = getattr(instance, field)

            if (
                # field has not been logged
                field not in logged_diff or
                # value doesn't match most recent log
                logged_diff[field]['now'] != value
            ):
                diff[field] = {'now': value}

        if diff:
            ChangeLog.objects.create(
                instance=instance,
                log_type=ChangeLog.ON_SYNC,
                fields=diff,
            )
