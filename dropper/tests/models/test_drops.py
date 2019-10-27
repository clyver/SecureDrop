from django.test import TestCase
from django.utils import timezone

from dropper.tests import factories


class TestDrop(TestCase):

    def test_create(self):
        """
        Confirm we can create a basic Drop.
        """
        drop = factories.Drop(text='foo')
        self.assertEqual(drop.text, 'foo')

    def test_attempt_retrieval(self):
        """
        Confirm by default we can retrieve a Drop once.
        """
        drop = factories.Drop()

        drop.attempt_retrieval()
        self.assertEqual(drop.times_retrieved, 1)

        drop.attempt_retrieval()
        drop.attempt_retrieval()

        self.assertEqual(drop.times_rejected, 2)

    def test_attempt_retrieval_with_limit(self):
        """
        Confirm we cannot retrieve a Drop more than its retrieval_limit
        """

        num_retrievals = 3
        drop = factories.Drop(retrieval_limit=num_retrievals)

        while num_retrievals:
            drop_retrieval = drop.attempt_retrieval()
            self.assertTrue(drop_retrieval.was_successful)
            num_retrievals -= 1

        drop_retrieval = drop.attempt_retrieval()
        self.assertFalse(drop_retrieval.was_successful)

    def test_attempt_retrieval_no_limit(self):
        """
        Confirm we can attempt numerous retrievals on a Drop with no retrieval_limit.
        """

        drop = factories.Drop(retrieval_limit=None)

        all_retrievals = [drop.attempt_retrieval() for _ in range(3)]
        self.assertTrue(all(retrieval.was_successful for retrieval in all_retrievals))

    def test_attempt_retrieval_expired(self):
        """
        Confirm we can not retrieve a Drop if it is past expiration.
        """

        one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
        drop = factories.Drop(expires_on=one_minute_ago)

        drop_retrieval = drop.attempt_retrieval()
        self.assertFalse(drop_retrieval.was_successful)

    def test_attempt_retrieval_with_password(self):
        """
        Confirm we can retrieve a Drop providing the proper password.
        """

        password = 'mySecretPassword'
        drop = factories.Drop(password=password)

        drop_retrieval = drop.attempt_retrieval(password='garbagePassword')
        self.assertFalse(drop_retrieval.was_successful)

        drop_retrieval = drop.attempt_retrieval(password=password)
        self.assertTrue(drop_retrieval.was_successful)

    def test_attempt_retrieval_rejection_limit_reached(self):
        """
        Confirm we can no longer retrieve a Drop once the rejection limit is reached.
        """

        password = 'anotherVerySecretPassword'
        rejection_limit = 2
        drop = factories.Drop(password=password, rejection_limit=rejection_limit, retrieval_limit=2)

        drop_retrieval = drop.attempt_retrieval(password=password)
        self.assertTrue(drop_retrieval.was_successful)

        while rejection_limit:
            drop_retrieval = drop.attempt_retrieval()
            self.assertFalse(drop_retrieval.was_successful)

            rejection_limit -= 1

        # Show that the Drop became locked even though we have yet to reach the retrieval limit.
        drop_retrieval = drop.attempt_retrieval(password=password)
        self.assertLess(drop.times_retrieved, drop.retrieval_limit)
        self.assertFalse(drop_retrieval.was_successful)
