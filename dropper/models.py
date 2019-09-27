from cryptography.fernet import Fernet
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.timezone import now


default_cipher = Fernet(settings.FERNET_KEY)


class DropQuerySet(models.QuerySet):

    def create(self, text=None, password=None, **kwargs):

        text = text or ''

        cipher = Fernet(password) if password else default_cipher
        kwargs['text'] = cipher.encrypt(text.encode())

        if password:
            kwargs['password'] = default_cipher.encrypt(password)

        return super().create(**kwargs)


class Drop(models.Model):
    """
    A piece of text with built-in safeguarding.
    """

    objects = DropQuerySet.as_manager()

    uuid = models.UUIDField(default=uuid.uuid4)
    text = models.BinaryField()

    password = models.CharField(null=True, blank=True, max_length=256)
    retrieval_limit = models.PositiveIntegerField(default=1, null=True, blank=True)
    rejection_limit = models.PositiveIntegerField(null=True, blank=True)
    expires_on = models.DateTimeField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    @property
    def is_retrievable(self):
        """
        Indicate if this Drop is eligible for retrieval.
        """

        if self.retrieval_limit is not None and self.times_retrieved >= self.retrieval_limit:
            return False

        if self.rejection_limit is not None and self.times_rejected < self.rejection_limit:
            return False

        if self.is_expired:
            return False

        return True

    def attempt_retrieval(self):
        """
        Record the attempted retrieval of this Drop.
        """

        return DropRetrieval.objects.create(drop=self, was_successful=self.is_retrievable)

    @property
    def times_retrieved(self):
        """
         Return the number of times retrieval was successful for this Drop.
        """

        return self.retrievals.successful().count()

    @property
    def times_rejected(self):
        """
        Return the number of times retrieval was rejected for this Drop.
        """

        return self.retrievals.rejected().count()

    @property
    def last_retrieved_on(self):
        """
        Return when this Drop was most last retrieved.
        """

        most_recent_retrieval = self.retrievals.successful().last()
        return most_recent_retrieval.created_on if most_recent_retrieval else None

    @property
    def is_expired(self):
        """
        A Drop is expired if its expires_on is set, and that time has past.
        """

        return self.expires_on and self.expires_on < now()

    @property
    def link(self):
        """
        The link that can be used to attempt retrieval of this Drop.
        """

        return reverse('get_link', kwargs={'drop_uuid': self.uuid})


class DropRetrievalManager(models.QuerySet):

    def successful(self):

        return self.filter(was_successful=True)

    def rejected(self):

        return self.filter(was_successful=False)


class DropRetrieval(models.Model):
    """
    A record of Drop retrieval attempts.
    """

    objects = DropRetrievalManager.as_manager()

    drop = models.ForeignKey(Drop, related_name='retrievals', on_delete=models.CASCADE)
    was_successful = models.BooleanField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
