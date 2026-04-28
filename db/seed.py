import random
from typing import List
from uuid import uuid4
from seniorProjectBackendDjango.db import BoidSchema
from firebase_admin import credentials
import firebase_admin
from firebase_admin import firestore

cred = credentials.Certificate('firebase_admin_sdk.json')
firebase_app = firebase_admin.initialize_app(cred)
firebase_db = firestore.client()


def addRandomBoid(array: list):
    color_section = lambda: random.randint(0, 255)
    array.append(
        BoidSchema(
            user_id=str(uuid4()),
            position_x=random.randint(1, 360),
            position_y=random.randint(1, 180),
            velocity_x=random.randint(-5, 5),
            velocity_y=random.randint(-5, 5),
            color="#%02X%02X%02X" % (color_section(), color_section(), color_section()),
        )
    )

    return array


def main():
    final_array: List[BoidSchema] = []
    num_of_boids = 25

    for _ in range(num_of_boids):
        addRandomBoid(final_array)

    for boid in final_array:
        firebase_db.collection("boids").add(boid.model_dump())

if __name__ == "__main__":
    main()
