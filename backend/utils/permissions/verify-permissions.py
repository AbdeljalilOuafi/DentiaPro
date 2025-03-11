import os
import sys
import django

# Getting the absolute path to the project root
# settings.py is in /home/ouafi/DentiaPro/backend/core/settings.py
# We need to add /home/ouafi/DentiaPro/backend to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))  # /permissions directory
utils_dir = os.path.dirname(current_dir)  # /utils directory
backend_dir = os.path.dirname(utils_dir)  # /backend directory

# Add the backend directory to Python path
sys.path.append(backend_dir)

# Now we can use core.settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Check existing permissions
print("All permissions:")
for p in Permission.objects.all():
    print(f"{p.content_type.app_label}.{p.codename}")

# Check content types
print("\nContent types:")
for ct in ContentType.objects.all():
    print(f"App: {ct.app_label}, Model: {ct.model}")