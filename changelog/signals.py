import datetime
from functools import wraps
import logging

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.models import signals
from django.dispatch import receiver
from psycopg2.extras import Json

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


def wrapped_update(f):
    """Decorator for use on <Manager>.update() method of tracked models

    This add a single additional query to the call, but does not load any
    model instances into memory in Python

    NOTE: This is fragile! If the ``ChangeLog`` model fields change, this
          will break.
    """

    if hasattr(f, 'im_self'):
        self = f.im_self
    else:
        self = f.__self__

    # Raw SQL query
    query = """
INSERT INTO changelog_changelog (
    created_at,
    object_id,
    fields,
    content_type_id,
    log_type
)
SELECT
    %s as created_at,
    "id" as object_id,
    %s as fields,
    %s as content_type_id,
    %s as log_type
from
    ({subquery}) as models
    """.format(
        # re-use the manager's query,
        subquery=str(self.all().only('id').query)
    )

    @wraps(f)
    def wrapper(**kwargs):
        num_rows_updated = f(**kwargs)

        models = get_tracked_models()
        diff = {
            field: {'now': kwargs[field]}
            for field in models[self.model]
            if field in kwargs
        }

        if diff:
            with connection.cursor() as c:
                c.execute(
                    query,
                    [
                        datetime.datetime.now(),
                        Json(diff),
                        ContentType.objects.get_for_model(self.model).pk,
                        ChangeLog.ON_UPDATE,
                    ],
                )

        return num_rows_updated

    return wrapper


def wrap_queryset_method(f):
    """Wrap a method that returns a QuerySet to return a patched QuerySet"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return patch_queryset(f(*args, **kwargs))

    return wrapper


def patch_queryset(qs):
    """Patch a QuerySet to log updates and to return patched QuerySets"""
    if getattr(qs, '__changelog_wrapped', False):
        return qs

    qs.__changelog_wrapped = True
    qs.update = wrapped_update(qs.update)

    # wrap all methods that return a queryset to propogate the update wrapper
    qs.all = wrap_queryset_method(qs.all)
    qs.filter = wrap_queryset_method(qs.filter)
    qs.exclude = wrap_queryset_method(qs.exclude)
    qs.annotate = wrap_queryset_method(qs.annotate)
    qs.order_by = wrap_queryset_method(qs.order_by)
    qs.reverse = wrap_queryset_method(qs.reverse)
    qs.distinct = wrap_queryset_method(qs.distinct)
    qs.all = wrap_queryset_method(qs.all)
    qs.select_related = wrap_queryset_method(qs.select_related)
    qs.prefetch_related = wrap_queryset_method(qs.prefetch_related)
    qs.extra = wrap_queryset_method(qs.extra)
    qs.defer = wrap_queryset_method(qs.defer)
    qs.only = wrap_queryset_method(qs.only)
    qs.using = wrap_queryset_method(qs.using)
    qs.select_for_update = wrap_queryset_method(qs.select_for_update)
    qs.raw = wrap_queryset_method(qs.raw)

    return qs


def patch_managers(**kwargs):
    """Patch the managers for all tracked models to log updates"""

    for model in get_tracked_models():
        for _, manager, abstract in model._meta.managers:
            patch_queryset(manager)
