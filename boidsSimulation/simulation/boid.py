from typing import List
import math
from pygame.math import Vector2
import random

WORLD_WIDTH = 360
WORLD_HEIGHT = 180

ALIGNMENT_PERCEPTION_RADIUS = 50
SEPERATION_PERCEPTION_RADIUS = 25
COHESION_PERCEPTION_RADIUS = 50

ALIGNMENT_STRENGTH = 2
COHESION_STRENGTH = 3
SEPERATION_STRENGTH = 5
MIN_SCALE_LENGTH = 1e-6


# TUNABLE CONSTANTS
class Boid:

    def __init__(
        self,
        userName = "",
        userID = "",
        color =  "",
        date_joined = "",
        position_x = random.randint(0, WORLD_WIDTH),
        position_y = random.randint(0, WORLD_HEIGHT),
        velocity_x = random.random(),
        velocity_y = random.random(),
        acceleration_x = 0,
        acceleration_y = 0,
    ) -> None:
        """
        Initialises a new Boid object with a random position and velocity
        within the bounds of the WORLD_WIDTH and WORLD_HEIGHT constants.
        The Boid's maximum force and speed are also set.
        """
        self.position = Vector2(position_x, position_y)
        self.velocity = Vector2(velocity_x, velocity_y)
        self.velocity.scale_to_length(random.randint(2, 4))
        self.acceleration = Vector2(acceleration_x, acceleration_y)

        self.maxForce = 0.2
        self.maxSpeed = 7

        self.color = color
        self.userID = userID
        self.userName = userName
        self.date_joined = date_joined

    def distance(self, point_1: Vector2, point_2: Vector2) -> float:
        """
        Calculates the Euclidean distance between two points in 2D space.

        Args:
            point_1 (Vector2): The first point.
            point_2 (Vector2): The second point.

        Returns:
            float: The Euclidean distance between the two points.
        """
        return math.sqrt((point_1.x - point_2.x) ** 2 + (point_1.y - point_2.y) ** 2)

    def limit_vector(self, vector: Vector2, max_force: float) -> Vector2:
        """
        Limits a vector's magnitude to a given maximum force.

        Args:
            vector (Vector2): The vector to limit.
            max_force (float): The maximum force the vector can have.

        Returns:
            Vector2: The vector with its magnitude limited to max_force.
        """

        # Is the vector magnitude greater than the max_force?
        if vector.length() > max_force:

            # Scale down to max_forse
            vector.scale_to_length(max_force)

        return vector

    def edges(self):
        """
        If the boid's position is at the edge of the screen, it is repositioned to the opposite edge.
        This is done by comparing the boid's position to the WORLD_WIDTH and WORLD_HEIGHT constants.
        If the boid is off the right edge, it is moved to the left edge and vice versa.
        The same applies to the y-axis, where if the boid is off the top edge it is moved to the bottom edge and vice versa.
        """

        if self.position.x > WORLD_WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WORLD_WIDTH

        if self.position.y > WORLD_HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = WORLD_HEIGHT

    def align(self, boids: List["Boid"]) -> Vector2:
        """
        Calculates the steering force for alignment with the average velocity of
        its neighbors within a given perception radius.

        Args:
            boids (List[Boid]): A list of Boid objects in the simulation.

        Returns:
            Vector2: The steering force for alignment.
        """

        # Zero the steering vector, total(for averaging), and set a perception radius
        steering = Vector2(0, 0)
        total = 0

        # For each of the boids inside the simulation
        for other_boid in boids:

            # This is the boid sprite, but we want the actual boid itself and calc distance
            d = self.distance(self.position, other_boid.position)

            # Is the given boid not itself and is the distance within the range of being seen?
            if self != other_boid and d < ALIGNMENT_PERCEPTION_RADIUS:

                # Add the other boids velecity to the steering for and add one to the total (needed for avg later)
                steering += other_boid.velocity
                total += 1

        # Have you seen any other boids?
        if total > 0:

            # Divide the steering my the total for average and cap it's speed
            steering /= total
            if steering.length() > MIN_SCALE_LENGTH:
                steering.scale_to_length(self.maxSpeed)

            # subtract our velocity and limit the the force
            steering -= self.velocity
            steering = self.limit_vector(steering, self.maxForce)

        return steering

    def seperation(self, boids: List["Boid"]) -> Vector2:
        """
        Calculates the steering force for seperation from its neighbors within a given perception radius.

        The seperation steering force is calculated by summing the difference vectors from
        the Boid to each of its neighbors, where the difference vector is divided by the
        square of the distance between the Boids. The sum is then normalized to the maximum
        speed of the Boid, and subtracted from the Boid's current velocity to obtain the
        steering force.

        Args:
            boids (List[BoidSprite]): A list of Boid objects in the simulation.

        Returns:
            Vector2: The steering force for seperation.
        """

        # Zero the steering vector, total(for averaging), and set a perception radius
        steering = Vector2(0, 0)
        total = 0

        # For every boid in the simulation
        for other_boid in boids:

            # This is the boid sprite, but we want the actual boid itself and calc distance
            d = self.distance(self.position, other_boid.position)

            # Is the given boid not itself and is the distance within the range of being seen?
            if self != other_boid and d < SEPERATION_PERCEPTION_RADIUS:

                # Calculate the difference vector from the Boid to its neighbor and divide it by
                # the square of the distance between them. This will give us the "repulsion" force
                # vector, where the closer the neighbor is, the stronger the force is.
                difference_vector = self.position - other_boid.position
                try:
                    difference_vector /= d * d
                except ZeroDivisionError:
                    difference_vector = Vector2(0, 0)

                steering += difference_vector
                total += 1

        # Have you seen any other boids?
        if total > 0:

            # Divide the steering vector by the total number of boids seen
            steering /= total
            # Scale this average to the maximum speed of the boid
            if steering.length() > MIN_SCALE_LENGTH:
                steering.scale_to_length(self.maxSpeed)
            # Subtract the boid's current velocity from this average
            steering -= self.velocity
            # Limit this force to the maximum force the boid can apply
            steering = self.limit_vector(steering, self.maxForce)

        return steering

    def cohesion(self, boids: List["Boid"]):
        """
        Calculates the steering force for cohesion to the average position of its neighbors within a given perception radius.

        The cohesion steering force is calculated by summing the positions of the Boid's neighbors,
        then dividing by the total number of neighbors seen. The steering force is then calculated
        by subtracting the Boid's current position and velocity from the average position of its neighbors.

        Args:
            boids (List[Boid]): A list of Boid objects in the simulation.

        Returns:
            Vector2: The steering force for cohesion.
        """

        # Zero the steering vector and total for averaging
        steering = Vector2(0, 0)
        total = 0

        # For each boid in the simulation
        for other_boid in boids:

            # Get the boid from the sprite and calculate distance between
            d = self.distance(self.position, other_boid.position)

            # This is the boid sprite, but we want the actual boid itself and calc distance
            if self != other_boid and d < COHESION_PERCEPTION_RADIUS:
                steering += other_boid.position
                total += 1

        # Have you seen any other boids?
        if total > 0:
            # Calculate the average position of the boids seen
            steering /= total
            # Calculate the steering force by subtracting the boid's current position
            steering -= self.position
            # Scale this average to the maximum speed of the boid
            if steering.length() > MIN_SCALE_LENGTH:
                steering.scale_to_length(self.maxSpeed)
            # Subtract the boid's current velocity from this average
            steering -= self.velocity
            # Limit this force to the maximum force the boid can apply
            steering = self.limit_vector(steering, self.maxForce)

        return steering

    def flock(self, boids: List["Boid"]):
        """
        Calculates the steering forces for flocking and applies them to the boid.

        The flocking algorithm is comprised of three main forces: Alignment, Seperation, and Cohesion.
        Alignment is the force that aligns the boids velocity with the average velocity of its neighbors.
        Seperation is the force that pushes boids away from each other.
        Cohesion is the force that pulls boids towards the average position of its neighbors.

        The strength of each force can be adjusted by setting the respective constant above.
        The final acceleration is the sum of the three forces, which is then used to update the boid's velocity.

        Args:
            boids (List[Boid]): A list of Boid objects in the simulation.
        """

        # Calls each piece of the algorithm
        alignment = self.align(boids)
        seperation = self.seperation(boids)
        cohesion = self.cohesion(boids)

        # Adds stength to each piece
        seperation *= SEPERATION_STRENGTH
        alignment *= ALIGNMENT_STRENGTH
        cohesion *= COHESION_STRENGTH

        # We apply to the accleration vector, which keeps the boid moving
        self.acceleration += seperation
        self.acceleration += cohesion
        self.acceleration += alignment

    # def draw(self):
    #     arcade.draw_circle_filled(self.position.x, self.position.y, 10, self.color)

    def update(self, boids: List["Boid"]):
        """
        Updates the boid's position and velocity based on its acceleration and maximum speed.

        The boid's acceleration is first added to its velocity, then the velocity is limited to the
        maximum speed of the boid. The acceleration is then reset to zero.
        """
        self.edges()
        self.flock(boids)

        self.position += self.velocity
        self.velocity += self.acceleration
        self.velocity = self.limit_vector(self.velocity, self.maxSpeed)
        self.acceleration *= 0

    def to_dict(self) -> dict:
        """
        Converts the Boid object to a dictionary, excluding maxForce and maxSpeed.
        """
        return {
            "user_id": self.userID,
            "color": self.color,
            "position_x": self.position.x,
            "position_y": self.position.y,
            "velocity_x": self.velocity.x,
            "velocity_y": self.velocity.y,
        }
