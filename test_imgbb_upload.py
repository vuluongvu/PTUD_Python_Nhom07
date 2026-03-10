import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webbapp.settings')
django.setup()

from users.views import upload_image_to_imgbb
import requests

try:
    with open('test_avatar.jpg', 'rb') as f:
        url = upload_image_to_imgbb(f)
        print("Upload Result:", url)
except Exception as e:
    print("Failed:", e)
