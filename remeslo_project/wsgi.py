import os

from django.core.wsgi import get_wsgi_application

import sys
print(">>> WSGI loaded!", file=sys.stderr)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'remeslo_project.settings')

application = get_wsgi_application()
