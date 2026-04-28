import os
import time
import threading
from typing import Dict, List

from pygame.math import Vector2
from boidsSimulation.simulation import boid
from boidsSimulation import models, services

from seniorProjectBackendDjango.db import BoidSchema
from seniorProjectBackendDjango.settings import firebase_db

BOID_DICT: Dict[str, boid.Boid] = {}
data_lock = threading.Lock()
GS_SPREADSHEET = os.getenv("GS_SPREADSHEET")
GS_WORKSHEET = "Boid"


class BoidsSimulation:
    def __init__(self):
        """
        Initialises a new BoidsSimulation window.

        The constructor sets the width, height, and title of the window, and sets
        the background color to a light blue. It also creates an empty list to store
        instances of BoidSprite objects.

        Args:
            None
        """
        self.time_elapsed = 0
        self._running = True
        self.db = services.GSGenericORM(GS_SPREADSHEET, GS_WORKSHEET, id_column="user_id")

    def load_boids_from_db(self):
        
        db_boids = firebase_db.collection("boids").stream()

        for db_boid in db_boids:
            db_boid_dict = BoidSchema(**db_boid.to_dict())
            sim_boid = boid.Boid(
                userName="hello",
                userID=db_boid_dict.user_id,
                date_joined="today",
                color=db_boid_dict.color,
                position_x=db_boid_dict.position_x,
                position_y=db_boid_dict.position_y,
                velocity_x=db_boid_dict.velocity_x,
                velocity_y=db_boid_dict.velocity_y,
                acceleration_x=0,
                acceleration_y=0
            )

            BOID_DICT[db_boid.id] = sim_boid
            
    def setup(self):
        """
        Sets up the simulation by creating a specified number of BoidSprite objects and
        adding them to the sprite list.

        This method is called once when the simulation is first set up. It is used to
        create the initial population of boids in the simulation.

        Args:
            None
        """
        self.load_boids_from_db()

    def update(self, delta_time):
        """
        Updates the position of all sprites in the sprite list using the Boids algorithm.

        This method is called once per frame, and is used to update the positions of all
        boids in the simulation. The Boids algorithm is implemented in the update method
        of the BoidSprite class.

        Args:
            delta_time (float): The time in seconds since the last frame was rendered.
        """

        # self.time_elapsed += delta_time
        # Update sprite movements (you can add your boid logic here later)
        for _, sprite in BOID_DICT.items():
            sprite.update(list(BOID_DICT.values()))

    def stop(self):
        self._running = False


class SimulationRunner:
    def __init__(self, simulation: BoidsSimulation):
        self.simulation = simulation
        self._last_update = time.time()
        self._running = True
        
    def run(self, fps: float = 1/60):
        """Run the simulation loop"""
        while self._running and self.simulation._running:
            current_time = time.time()
            delta_time = current_time - self._last_update
            
            # Update simulation with actual delta time
            with data_lock:
                self.simulation.update(delta_time)
            
            # Sleep to maintain approximately 60 FPS
            sleep_time = max(0, fps - delta_time)
            time.sleep(sleep_time)
            
            self._last_update = current_time
            
    def stop(self):
        """Stop the simulation loop"""
        self._running = False