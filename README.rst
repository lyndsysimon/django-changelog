=========
Changelog
=========

Django-changelog is a simple app that automates the creation of log entries when Django models changes.

Quick Start
-----------

1. Add ``'changelog'`` to your ``INSTALLED_APPS`` in settings.

2. Add ``CHANGELOG_TRACKED_FIELDS`` to your settings::

    CHANGELOG_TRACKED_FIELDS = {
        'myapp.MyModel': (
            'first_field_to_track',
            'second_field_to_track',
        ),
    }

3. Run ``./manage.py migrate`` to create the required tables.
