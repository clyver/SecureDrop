from factory import DjangoModelFactory, sequence

from dropper import models as dropper_models


class Drop(DjangoModelFactory):

    class Meta:
        model = dropper_models.Drop

    text = sequence(lambda n: 'My text: {}'.format(n))
