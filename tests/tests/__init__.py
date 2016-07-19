from django.test import TestCase

from tests import models


class BaseTestCase(TestCase):

    def tearDown(self):
        models.TrackedModel.objects.all().delete()
        models.UntrackedModel.objects.all().delete()
