from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models


class ChangeLog(models.Model):
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

    def __repr__(self):
        return '<ChangeLog {pk}: {model_name}:{instance_id}>'.format(
            pk=self.pk,
            model_name=self.instance._meta.label,
            instance_id=self.object_id,
        )
