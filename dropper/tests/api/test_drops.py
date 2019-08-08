from django.test import TestCase

from dropper.models import Drop
from dropper.tests import factories


class TestDrop(TestCase):

    create_url = '/drop/'
    retrieve_url = '{}{}'.format(create_url, '{}')

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
        message = 'My special secret!'

        existing_count = Drop.objects.count()

        response = self.client.post(self.create_url, {'message': message})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Drop.objects.count(), existing_count + 1)

        drop = Drop.objects.last()
        self.assertEqual(drop.text, message)

    def test_retrieve_fails_on_invalid_uuid(self):
        """
        Confirm we get a 404 when attempting to fetch an invalid Drop.
        """

        response = self.client.get(self.retrieve_url.format('junk_uuid'))
        self.assertEqual(response.status_code, 404)

    def test_retrieve(self):
        """
        Confirm we can retrieve a Drop via its uuid.
        """

        drop = factories.Drop(text='retrieve me!')

        self.assertIsNone(drop.last_retrieved_on)
        existing_count = Drop.objects.count()

        response = self.client.get(self.retrieve_url.format(drop.uuid))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Drop.objects.count(), existing_count)
        self.assertIn(drop.text, response.json().get('text'))

        drop.refresh_from_db()
        self.assertIsNotNone(drop.last_retrieved_on)
