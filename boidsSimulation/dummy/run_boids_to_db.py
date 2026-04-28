import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seniorProjectBackendDjango.settings')

# Initialize Django
django.setup()

from boidsSimulation.models import Boid
from boidsSimulation.serializers import BoidSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

USER_NAMES = [
    "Arthur Morgan",
    "Dutch van der Linde",
    "John Marston",
    "Sadie Adler",
    "Micah Bell",
    "Hosea Matthews",
    "Bill Williamson",
    "Charles Smith",
    "Javier Escuella",
    "Lenny Summers"
]

for i, userName in enumerate(USER_NAMES):

    Boid.objects.update_or_create(
        userID = f"{userName}#{i}",
        defaults={
            'userName': userName,
            'userID': f"{userName}#{i}",
            'velocity_x': 1.0,
            'velocity_y': 1.0
        }
    )
