from django.contrib import admin

from changelog import models


class ChangeLogAdmin(admin.ModelAdmin):
    list_display = (
        'organization',
        'content_type',
        'fields_changed',
        'created_at',
    )
    readonly_fields = (
        'content_type',
        'object_id',
        'fields',
        'created_at',
    )

    def organization(self, instance):
        return instance.instance.organization

    def fields_changed(self, instance):
        return '\n'.join(sorted(instance.fields.keys()))


admin.site.register(models.ChangeLog, ChangeLogAdmin)
