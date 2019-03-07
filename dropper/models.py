import uuid

from django.db import models
from django.urls import reverse
from django.utils.timezone import now


class Drop(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4)
    text = models.TextField()

    created_on = models.DateTimeField(auto_now_add=True)
    last_retrieved_on = models.DateTimeField(null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)

    def mark_retrieved(self):
        self.last_retrieved_on = now()
        self.save()

    @property
    def link(self):
        return reverse('get_link', kwargs={'drop_uuid': self.uuid})
