from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from dropper.models import Drop
from dropper.tests import factories


class TestDrop(TestCase):

    create_url = '/drop/'

    def test_create_fails_without_message(self):
        """
        Confirm we get a 400 when we attempt to create a Drop without a message
        """
        existing_count = Drop.objects.count()

        response = self.client.post(self.create_url, {'dummy_key': 'dummy_value'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Drop.objects.count(), existing_count)

    def test_create(self):
        """
        Confirm we can create a new Drop.
        """
        creation_data = {
            'text': 'My special secret!',
            'password': 'YouWillNeverGuess123',
            'retrieval_limit': 4,
            'rejection_limit': 2,
            'expires_on': timezone.now().date().isoformat()
        }

        existing_count = Drop.objects.count()

        response = self.client.post(self.create_url, creation_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Drop.objects.count(), existing_count + 1)

        drop = Drop.objects.last()

        self.assertEqual(creation_data.pop('expires_on'), drop.expires_on.isoformat())

        for key, val in creation_data.items():
            self.assertEqual(getattr(drop, key), val)

    def test_retrieve_fails_on_invalid_uuid(self):
        """
        Confirm we get a 404 when attempting to fetch an invalid Drop.
        """

        response = self.client.post(reverse('get_drop', kwargs={'drop_uuid': 'junk_uiud'}))
        self.assertEqual(response.status_code, 404)

    def test_retrieve(self):
        """
        Confirm we can retrieve a Drop via its uuid.
        """

        drop = factories.Drop(text='retrieve me!')

        self.assertIsNone(drop.last_retrieved_on)
        existing_count = Drop.objects.count()

        response = self.client.post(drop.link)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Drop.objects.count(), existing_count)
        self.assertIn(response.json().get('text'), drop.text)

        drop.refresh_from_db()
        self.assertIsNotNone(drop.last_retrieved_on)

    def test_retrieve_forbidden(self):
        """
        Confirm we get a 403 when attempting to retrieve a Drop that is no longer retrievable.
        """

        drop = factories.Drop(retrieval_limit=1)

        response = self.client.post(drop.link)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(drop.link)
        self.assertEqual(response.status_code, 403)

    def test_retrieve_with_password(self):
        """
        Confirm we can retrieve a Drop providing the proper password.
        """

        password = 'password123!'
        drop = factories.Drop(password=password)

        response = self.client.post(drop.link, {'password': 'garbage-password'})
        self.assertEqual(response.status_code, 403)

        response = self.client.post(drop.link, {'password': password})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('text'), drop.text)
