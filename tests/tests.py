from django.test import TestCase


class ExampleTestCase(TestCase):
    def test_nothing(self):
        self.assertEqual(1, 1)

    def test_another_nothing(self):
        self.assertEqual(2, 2)
