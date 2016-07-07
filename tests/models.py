from django.db import models


class TrackedModel(models.Model):

    tracked_char = models.CharField(max_length=256, null=True)
    untracked_char = models.CharField(max_length=256)


class UntrackedModel(models.Model):
    pass
