from __future__ import absolute_import

from django.db import connection

from tests import factories
from tests.models import TrackedModel
from tests.tests import BaseTestCase
from changelog.models import ChangeLog
from changelog.utils import create_sync_logs


class CreateSyncLogTestCase(BaseTestCase):
    def setUp(self):
        super(CreateSyncLogTestCase, self).setUp()
        self.instance = factories.TrackedModelFactory(
            tracked_char='initial value',
        )

    def test_no_logs(self):
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

    def test_no_changes(self):
        self.instance.tracked_char = 'logged value'
        self.instance.save()

        create_sync_logs(TrackedModel)

        self.assertEqual(
            0,
            ChangeLog.objects.filter(log_type=ChangeLog.ON_SYNC).count(),
        )

    def test_changes(self):
        self.instance.tracked_char = 'logged value'
        self.instance.save()

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

    def test_queryset(self):
        excluded = factories.TrackedModelFactory()
        queryset = TrackedModel.objects.exclude(id=excluded.id)

        create_sync_logs(queryset=queryset)

        log = ChangeLog.objects.filter(log_type=ChangeLog.ON_SYNC).get()

        self.assertEqual(
            self.instance,
            log.instance,
        )
