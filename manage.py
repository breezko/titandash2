#!/usr/bin/env python

import os
import sys

if __name__ == "__main__":
    # Main entry point for our manage.py script.
    # Ensure our settings module is set correctly.
    os.environ.setdefault(key="DJANGO_SETTINGS_MODULE", value="settings")

    from django.core.management import execute_from_command_line

    # Attempt to execute whatever django command has been
    # specified, more than likely, we just want to use orm.
    execute_from_command_line(argv=sys.argv)
