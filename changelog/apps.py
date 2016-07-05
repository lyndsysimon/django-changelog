from __future__ import unicode_literals
import logging

from django.apps import AppConfig


logger = logging.getLogger(__name__)


class ChangelogConfig(AppConfig):
    def ready(self):
        import changelog.signals  # noqa

    name = 'changelog'
