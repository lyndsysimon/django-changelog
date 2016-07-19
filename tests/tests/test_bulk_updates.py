from changelog.models import ChangeLog
from tests import factories
from tests.models import TrackedModel
from tests.tests import BaseTestCase


class BulkUpdateTestCase(BaseTestCase):
    def setUp(self):
        self.tracked = [
            factories.TrackedModelFactory(),
            factories.TrackedModelFactory(),
            factories.TrackedModelFactory(),
        ]

    def test_update_all(self):
        TrackedModel.objects.update(tracked_char='asdf')

        self.assertEqual(
            3,
            ChangeLog.objects.count(),
        )

        log = ChangeLog.objects.order_by('object_id').first()

        self.assertEqual(
            self.tracked[0],
            log.instance,
        )

    def test_update_one(self):
        TrackedModel.objects.filter(
            id=self.tracked[0].id
        ).update(tracked_char='asdf')

        self.assertEqual(
            1,
            ChangeLog.objects.count(),
        )

        log = ChangeLog.objects.get()

        self.assertEqual(
            self.tracked[0],
            log.instance,
        )
