from factory import DjangoModelFactory

from dropper import models as dropper_models


class Drop(DjangoModelFactory):

    class Meta:
        model = dropper_models.Drop
