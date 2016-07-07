from __future__ import absolute_import

from django.conf import settings
from django.test import TestCase

from . import factories
from .models import TrackedModel, UntrackedModel
from changelog.models import ChangeLog


class ChangelogTestCase(TestCase):
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
