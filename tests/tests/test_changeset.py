from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType

from tests import factories
from tests.tests import BaseTestCase
from changelog.models import ChangeLog, ChangeSet


class ChangeSetTestCase(BaseTestCase):
    def setUp(self):
        self.tracked = factories.TrackedModelFactory(
            tracked_char='first value'
        )
        self.tracked.tracked_char = 'second value'
        self.tracked.save()
        self.tracked.tracked_char = 'third value'
        self.tracked.save()
        self.tracked.tracked_char = 'fourth value'
        self.tracked.save()
        self.tracked.tracked_char = 'fifth value'
        self.tracked.save()
        self.tracked.tracked_char = 'sixth value'
        self.tracked.save()
        self.logs = list(
            ChangeLog.objects.filter(
                content_type=ContentType.objects.get_for_model(self.tracked),
                object_id=self.tracked.pk,
            ).order_by('created_at').all()
        )

    def test_init_instance_param(self):
        x = ChangeSet(instance=self.tracked)

        self.assertEqual(
            self.tracked.pk,
            x.instance.pk,
        )

    def test_init_first_param(self):
        x = ChangeSet(first=self.logs[2])

        self.assertEqual(
            self.logs[2].pk,
            x.first.pk,
        )

        self.assertEqual(
            self.logs[-1].pk,
            x.last.pk,
        )

        self.assertEqual(
            self.tracked,
            x.instance,
        )

    def test_init_last_param(self):
        x = ChangeSet(last=self.logs[2])

        self.assertEqual(
            self.logs[2].pk,
            x.last.pk,
        )

        self.assertEqual(
            self.logs[0].pk,
            x.first.pk,
        )

        self.assertEqual(
            self.tracked,
            x.instance,
        )

    def test_init_param_mismatch(self):
        other = factories.TrackedModelFactory()
        other.tracked_char = 'first value'
        other.save()
        other.tracked_char = 'second value'
        other.save()

        other_logs = list(
            ChangeLog.objects.filter(
                content_type=ContentType.objects.get_for_model(other),
                object_id=other.pk,
            ).order_by('created_at').all()
        )

        # instance param is from another instance
        with self.assertRaises(AssertionError):
            ChangeSet(
                instance=other,
                first=self.logs[0],
                last=self.logs[-1],
            )

        # first param is from another instance
        with self.assertRaises(AssertionError):
            ChangeSet(
                instance=self.tracked,
                first=other_logs[0],
                last=self.logs[-1],
            )

        # last param is from another instance
        with self.assertRaises(AssertionError):
            ChangeSet(
                instance=self.tracked,
                first=self.logs[0],
                last=other_logs[0],
            )

    def test_iter_logs(self):
        x = ChangeSet(instance=self.tracked)

        self.assertEqual(
            self.logs,
            list(x.iter_logs()),
        )

    def test_iter_logs_subset(self):
        x = ChangeSet(
            first=self.logs[1],
            last=self.logs[3],
        )

        self.assertEqual(
            self.logs[1:4],
            list(x.iter_logs()),
        )

    def test_diff(self):
        x = ChangeSet(instance=self.tracked)
        expected = {
            'tracked_char': {
                'was': 'first value',
                'now': 'sixth value',
            },
        }

        self.assertEqual(
            expected,
            x.diff,
        )

    def test_diff_subset(self):
        x = ChangeSet(
            first=self.logs[1],
            last=self.logs[3],
        )
        expected = {
            'tracked_char': {
                'was': 'second value',
                'now': 'fifth value',
            },
        }

        self.assertEqual(
            expected,
            x.diff,
        )

    def test_diff_no_logs(self):
        x = ChangeSet(
            instance=factories.TrackedModelFactory()
        )

        self.assertEqual(
            {},
            x.diff,
        )
