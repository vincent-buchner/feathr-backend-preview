from rest_framework import serializers
from boidsSimulation.models import Boid


class BoidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boid
        fields = [
            "userID",
            "userName",
            "color",
            "dateJoined",
            "position_x",
            "position_y",
            "velocity_x",
            "velocity_y",
            "acceleration_x",
            "acceleration_y",
        ]
