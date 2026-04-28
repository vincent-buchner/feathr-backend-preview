from django.db import models

# Create your models here.
class Boid(models.Model):

    dateJoined = models.DateTimeField(auto_now_add=True)
    userName = models.CharField(max_length=100, blank=False)
    userID = models.CharField(max_length=100, blank=False, null=False, primary_key=True)
    color = models.CharField(max_length=7, blank=True, default="#A63E26")

    # Simulation Based Details
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    velocity_x = models.FloatField(default=0.0)
    velocity_y = models.FloatField(default=0.0)
    acceleration_x = models.FloatField(default=0.0)
    acceleration_y = models.FloatField(default=0.0)

    class Meta:
        ordering = ['dateJoined']
