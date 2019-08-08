from django.test import TestCase

from dropper.tests import factories


class TestDrop(TestCase):

    def test_crete_empty(self):
        """
        Confirm we can create a Drop without any supplementary data.
        """
        drop = factories.Drop()
        self.assertEqual(drop.text, '')

    def test_mark_retrieved(self):
        """
        Confirm we set last_retrieved_on when mark_retrieved() is called.
        """
        drop = factories.Drop()
        self.assertIsNone(drop.last_retrieved_on)

        drop.mark_retrieved()
        self.assertIsNotNone(drop.last_retrieved_on)
