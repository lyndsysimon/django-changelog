from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q


class ChangeLog(models.Model):

    ON_SAVE = 0
    ON_UPDATE = 1
    ON_SYNC = 2
    LOG_TYPE_CHOICES = (
        (ON_SAVE, 'On Save'),
        (ON_SAVE, 'On Update'),
        (ON_SAVE, 'On Sync'),
    )
    log_type = models.PositiveSmallIntegerField(
        choices=LOG_TYPE_CHOICES,
        default=ON_SAVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    instance = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id',
    )

    fields = JSONField()
    # Nested dict in the format:
    # {
    #     '<field_name>': {
    #         'was': '<old value>',
    #         'now': '<new value>',
    #     }
    # }
    # Note that some log types may not include the 'was' key.

    def __repr__(self):
        return '<ChangeLog {pk}: {model_name}:{instance_id}>'.format(
            pk=self.pk,
            model_name=self.instance._meta.label,
            instance_id=self.object_id,
        )


class ChangeSet(object):
    def __init__(self, first=None, last=None, instance=None):
        """A summary of changes to tracked fields between two states.

        Any combination of parameters may be passed, provided they refer to
        the same model instance.

        If only ``instance`` is passed, then all ``ChangeLogs`` will be
        included.

        If only ``first`` is passed, then all ``ChangeLog``s after will be
        included. Likewise, if only ``last`` is passed, then all
        ``ChangeLog``s prior will be included.

        :param first:
        :param last:
        :param instance:
        """

        if not any((first, last, instance)):
            raise TypeError("At least one keyword argument must be provided.")

        # ensure all params refer to the same instance

        if instance is not None:
            if first is not None:
                assert first.instance.pk == instance.pk
            if last is not None:
                assert last.instance.pk == instance.pk

        if first is not None:
            if last is not None:
                assert last.instance.pk == first.instance.pk

        # set instance variables

        self.instance = instance
        self.first = first
        self.last = last

        if self.instance is None:
            self.instance = (self.first or self.last).instance

        if self.first is None:
            self.first = ChangeLog.objects.filter(
                content_type=ContentType.objects.get_for_model(self.instance),
                object_id=self.instance.pk,
            ).order_by('created_at').first()

        if self.last is None:
            self.last = ChangeLog.objects.filter(
                content_type=ContentType.objects.get_for_model(self.instance),
                object_id=self.instance.pk,
            ).order_by('-created_at').first()

    def iter_logs(self):
        """Return a generator that yields ``ChangeLog``s, in chrono order"""
        query = Q(
            content_type=ContentType.objects.get_for_model(self.instance),
            object_id=self.instance.pk,
        )

        # values will not be set if no logs exist
        if self.first is not None and self.last is not None:
            query &= Q(
                created_at__gte=self.first.created_at,
                created_at__lte=self.last.created_at
            )

        return ChangeLog.objects.filter(query).order_by('created_at').all()

    @property
    def diff(self):
        diff = {}
        for log in self.iter_logs():
            for field in log.fields:
                if field not in diff:
                    diff[field] = log.fields[field]
                else:
                    diff[field]['now'] = log.fields[field]['now']
        return diff
