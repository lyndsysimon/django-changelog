from __future__ import absolute_import

import factory

from . import models


class TrackedModelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TrackedModel

    tracked_char = factory.Sequence(lambda n: 'value-{}'.format(n))
    untracked_char = factory.Sequence(lambda n: 'value-{}'.format(n))


class UntrackedModelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TrackedModel
