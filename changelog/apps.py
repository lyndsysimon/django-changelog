from __future__ import unicode_literals
import logging

from django.apps import AppConfig
from django.db.models import signals


logger = logging.getLogger(__name__)


class ChangelogConfig(AppConfig):
    def ready(self):
        import changelog.signals  # noqa

        changelog.signals.patch_managers()
        signals.post_migrate.connect(
            receiver=changelog.signals.patch_managers,
            dispatch_uid='changelog.patch_managers',
        )

    name = 'changelog'
