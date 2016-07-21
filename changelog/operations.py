from django.contrib.contenttypes.models import ContentType
from django.db.migrations.operations import RunPython

from changelog.utils import create_sync_logs


class InitialChangeLogSync(RunPython):

    def __init__(self, model_name, app_label=None):

        self.model_name = model_name
        self.app_label = app_label
        super(InitialChangeLogSync, self).__init__(
            code=self._create_logs,
            # TODO: Include a reverse_code method
        )

    def database_forwards(self,
                          app_label,
                          schema_editor,
                          from_state,
                          to_state):
        if self.app_label is None:
            self.app_label = app_label
        return super(InitialChangeLogSync, self).database_forwards(
            app_label=app_label,
            schema_editor=schema_editor,
            from_state=from_state,
            to_state=to_state,
        )

    def database_backwards(self,
                           app_label,
                           schema_editor,
                           from_state,
                           to_state):
        if self.app_label is not None:
            self.app_label = app_label
        return super(InitialChangeLogSync, self).database_backwards(
            app_label=app_label,
            schema_editor=schema_editor,
            from_state=from_state,
            to_state=to_state,
        )

    def _create_logs(self, apps, schema_editor):
        content_type = ContentType.objects.get_for_model(
            apps.get_model(self.app_label, self.model_name)
        )
        TrackedModel = content_type.model_class()
        create_sync_logs(TrackedModel)

    def _remove_logs(self, apps, schema_editor):
        content_type = ContentType.objects.get_for_model(
            apps.get_model(self.app_label, self.model_name)
        )
        TrackedModel = content_type.model_class()
        ChangeLog = apps.get_model('changelog', 'changelog')

        ChangeLog.objects.filter(
            log_type=ChangeLog.ON_SYNC,
            content_type=content_type,
        )