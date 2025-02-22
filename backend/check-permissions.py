#!/usr/bin/env python3
"""check-permissions module"""

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # Adjust if necessary
django.setup()



from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from users.models import User

# Add this somewhere (maybe in a management command or shell)
content_type = ContentType.objects.get_for_model(User)
permissions = Permission.objects.filter(content_type=content_type)
print("Available User permissions:", [p.codename for p in permissions])