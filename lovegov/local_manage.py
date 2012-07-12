import socket

# are we local?
LOCAL = False
if "lg" not in socket.getfqdn():
    LOCAL = True

#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lovegov.local_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
