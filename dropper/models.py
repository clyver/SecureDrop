import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from fernet_fields import EncryptedTextField


class DropQuerySet(models.QuerySet):

    def create(self, **kwargs):

        if not kwargs.get('text'):
            raise ValidationError('Must provide text to create a Drop.')

        return super().create(**kwargs)


class Drop(models.Model):
    """
    A piece of text with built-in safeguarding.
    """

    objects = DropQuerySet.as_manager()

    uuid = models.UUIDField(default=uuid.uuid4)
    text = EncryptedTextField()

    password = EncryptedTextField(null=True, blank=True)
    retrieval_limit = models.PositiveIntegerField(default=1, null=True, blank=True)
    rejection_limit = models.PositiveIntegerField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def is_retrievable(self, password=None):
        """
        Indicate if this Drop is eligible for retrieval.
        """

        if self.retrieval_limit is not None and self.times_retrieved >= self.retrieval_limit:
            return False

        if self.rejection_limit is not None and self.times_rejected >= self.rejection_limit:
            return False

        if self.is_expired:
            return False

        if self.password and self.password != password:
            return False

        return True

    def attempt_retrieval(self, password=None):
        """
        Record the attempted retrieval of this Drop.
        """

        return DropRetrieval.objects.create(drop=self, was_successful=self.is_retrievable(password=password))

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

        return reverse('get_drop', kwargs={'drop_uuid': self.uuid})


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
