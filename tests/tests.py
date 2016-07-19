from __future__ import absolute_import

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from . import factories
from .models import TrackedModel, UntrackedModel
from changelog.models import ChangeLog, ChangeSet


class ChangeLogTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        TrackedModel.objects.all().delete()
        UntrackedModel.objects.all().delete()

    def test_no_log_for_initial_creation(self):
        factories.TrackedModelFactory()

        self.assertEqual(
            0,
            ChangeLog.objects.count()
        )

    def test_tracked_field_logged(self):
        x = factories.TrackedModelFactory()
        x.tracked_char = 'asdf'
        x.save()

        self.assertEqual(
            1,
            ChangeLog.objects.count()
        )

    def test_char_field_was_none(self):
        x = factories.TrackedModelFactory(tracked_char=None)
        x.tracked_char = 'new value'
        x.save()

        log = ChangeLog.objects.get()

        self.assertIsNone(
            log.fields['tracked_char']['was']
        )

    def test_char_field_now_none(self):
        x = factories.TrackedModelFactory()
        x.tracked_char = None
        x.save()

        log = ChangeLog.objects.get()

        self.assertIsNone(
            log.fields['tracked_char']['now']
        )

    def test_char_field_correct(self):
        x = factories.TrackedModelFactory()
        x.tracked_char = 'new value'
        x.save()

        log = ChangeLog.objects.get()

        self.assertEqual(
            log.fields,
            {
                'tracked_char': {
                    'was': 'value-0',
                    'now': 'new value',
                }
            }
        )

class ChangeSetTestCase(TestCase):
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

    def tearDown(self):
        TrackedModel.objects.all().delete()

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
