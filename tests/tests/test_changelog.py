from __future__ import absolute_import

from tests import factories
from tests.tests import BaseTestCase
from changelog.models import ChangeLog


class ChangeLogTestCase(BaseTestCase):
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
        x = factories.TrackedModelFactory(
            tracked_char='initial value'
        )
        x.tracked_char = 'new value'
        x.save()

        log = ChangeLog.objects.get()

        self.assertEqual(
            log.fields,
            {
                'tracked_char': {
                    'was': 'initial value',
                    'now': 'new value',
                }
            }
        )