from __future__ import absolute_import

from django.db import connection
from django.test import TestCase

from tests import factories
from tests.models import TrackedModel
from changelog.models import ChangeLog
from changelog.utils import create_sync_logs


class ChangeSetTestCase(TestCase):
    def test_create_sync_logs_with_no_logs(self):
        factories.TrackedModelFactory(
            tracked_char='initial value',
        )

        create_sync_logs(TrackedModel)

        log = ChangeLog.objects.get()

        self.assertEqual(
            {
                'tracked_char': {'now': 'initial value'},
            },
            log.fields,
        )

        self.assertEqual(
            ChangeLog.ON_SYNC,
            log.log_type,
        )

    def test_create_sync_log_with_no_changes(self):
        instance = factories.TrackedModelFactory(
            tracked_char='initial value',
        )

        instance.tracked_char = 'logged value'
        instance.save()

        create_sync_logs(TrackedModel)

        self.assertEqual(
            0,
            ChangeLog.objects.filter(log_type=ChangeLog.ON_SYNC).count(),
        )

    def test_create_sync_log_with_changes(self):
        instance = factories.TrackedModelFactory(
            tracked_char='initial value',
        )

        instance.tracked_char = 'logged value'
        instance.save()

        connection.cursor().execute(
            "UPDATE tests_trackedmodel SET tracked_char = 'manual value'"
        )

        create_sync_logs(TrackedModel)

        log = ChangeLog.objects.filter(log_type=ChangeLog.ON_SYNC).get()

        self.assertEqual(
            {
                'tracked_char': {'now': 'manual value'}
            },
            log.fields,
        )
