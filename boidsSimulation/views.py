from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List
from google.cloud.firestore import DocumentReference
import json
import os
import random
from django.http import HttpRequest, JsonResponse
from pydantic import Json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView

from firebase_admin import firestore, auth
from boidsSimulation.services import is_validate_google_token_id
from seniorProjectBackendDjango.settings import SIMULATION_FPS, firebase_db
from seniorProjectBackendDjango.db import BoidSchema
from boidsSimulation.simulation.boid import (
    ALIGNMENT_PERCEPTION_RADIUS,
    ALIGNMENT_STRENGTH,
    COHESION_PERCEPTION_RADIUS,
    COHESION_STRENGTH,
    SEPERATION_PERCEPTION_RADIUS,
    SEPERATION_STRENGTH,
    WORLD_HEIGHT,
    WORLD_WIDTH,
    Boid,
)
from boidsSimulation.simulation.run import BOID_DICT, data_lock

GS_SPREADSHEET = os.getenv("GS_SPREADSHEET")
GS_WORKSHEET = "Boid"


@api_view()
def simulation_config(request):
    with data_lock:
        return JsonResponse(
            {
                "WORLD_WIDTH": WORLD_WIDTH,
                "WORLD_HEIGHT": WORLD_HEIGHT,
                "ALIGNMENT_PERCEPTION_RADIUS": ALIGNMENT_PERCEPTION_RADIUS,
                "SEPERATION_PERCEPTION_RADIUS": SEPERATION_PERCEPTION_RADIUS,
                "COHESION_PERCEPTION_RADIUS": COHESION_PERCEPTION_RADIUS,
                "ALIGNMENT_STRENGTH": ALIGNMENT_STRENGTH,
                "COHESION_STRENGTH": COHESION_STRENGTH,
                "SEPERATION_STRENGTH": SEPERATION_STRENGTH,
                "MIN_SCALE_LENGTH": 1e-6,
                "FPS": SIMULATION_FPS,
            }
        )


class CreateOrQueryUserBoid(APIView):
    def __init__(self) -> None:
        super().__init__()

    @dataclass
    class UserBoidResponse:
        message: str
        boid_id: str
        errors: List[str] = None

    def __post_init__(self):
        # Initialize errors as empty list if None
        if self.errors is None:
            self.errors = []

    def post(self, request: HttpRequest):

        try:

            # Parsed the data and get the the needed values
            data: dict = json.loads(request.body)
            id_token = data.get("id_token")
            user_id = data.get("user_id")

            # If we have neither the id_token or the user, return error
            if not id_token and not user_id:
                return JsonResponse(
                    asdict(
                        CreateOrQueryUserBoid.UserBoidResponse(
                            message="No id_token and user_id",
                            boid_id="",
                            errors=["Missing id_token and user_id"],
                        )
                    )
                )

            try:

                # Check to see if the given id_token is valid, and if it's not throw error
                if not is_validate_google_token_id(id_token, user_id):
                    return JsonResponse(
                        asdict(
                            CreateOrQueryUserBoid.UserBoidResponse(
                                message="Not Valid Token",
                                boid_id="",
                                errors=["Invalid Token"],
                            )
                        )
                    )

                # Create client and get the users boid
                db = firebase_db
                boid_ref = db.collection("boids").where("user_id", "==", user_id)
                boid_docs = boid_ref.get()

                # If that boid exists, return
                if boid_docs:  # This will be True if boid_docs is not empty
                    return JsonResponse(
                        asdict(
                            CreateOrQueryUserBoid.UserBoidResponse(
                                message="Boid exists",
                                boid_id=boid_docs[0].id,
                                errors=[],
                            )
                        )
                    )

                # Here we create the boid in the db
                color_section = lambda: random.randint(0, 255)
                user_color = "#%02X%02X%02X" % (
                    color_section(),
                    color_section(),
                    color_section(),
                )
                new_user_boid = BoidSchema(
                    user_id=user_id,
                    color=user_color,
                    position_x=random.randint(1, 360),
                    position_y=random.randint(1, 180),
                    velocity_x=random.randint(-5, 5),
                    velocity_y=random.randint(-5, 5),
                )
                updated_time_and_ref = firebase_db.collection("boids").add(
                    new_user_boid.model_dump()
                )
                boid_ref: DocumentReference = updated_time_and_ref[1]
                auth_user = auth.get_user(user_id)

                # If the boid doesn't exist, we add it
                with data_lock:
                    BOID_DICT[boid_ref.id] = Boid(
                        auth_user.display_name,
                        user_id,
                        user_color,
                        "today",
                        position_x=random.randint(1, 360),
                        position_y=random.randint(1, 180),
                        velocity_x=random.randint(-5, 5),
                        velocity_y=random.randint(-5, 5),
                    )

                return JsonResponse(
                    asdict(
                        CreateOrQueryUserBoid.UserBoidResponse(
                            message="Created new user boid",
                            boid_id=boid_ref.id,
                            errors=[],
                        )
                    )
                )

            except Exception as e:
                print(e)
                return JsonResponse(
                    asdict(
                        CreateOrQueryUserBoid.UserBoidResponse(
                            message="Error adding boid to db and simulation",
                            boid_id="",
                            errors=[str(e)],
                        )
                    )
                )
        except Exception as e:
            print(e)
            return JsonResponse(
                asdict(
                    CreateOrQueryUserBoid.UserBoidResponse(
                        message="Error has occured",
                        boid_id="",
                        errors=[str(e)],
                    )
                )
            )
class SingleBoidFromDB(APIView):

    def __init__(self) -> None:
        super().__init__()

        # self.db = GSGenericORM(GS_SPREADSHEET, GS_WORKSHEET, id_column="user_id")

    def get(self, request, pk):
        boid_ref = firebase_db.collection("boids").document(pk)
        boid = boid_ref.get()

        if boid.exists:
            return JsonResponse(boid.to_dict())
        else:
            return JsonResponse(
                {
                    "message": f"Couldn't get boid from db - Status: {boid}",
                }
            )

    def delete(self, request, pk):
        try:
            # success, message = self.db.delete(pk)
            firebase_db.collection("boids").document(pk).delete()

            return Response(status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:

            if not request.data:
                return Response(
                    {"error": "No data provided. Please include the required fields."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            boid_ref = firebase_db.collection("boids").document(pk)
            boid_ref.update(BoidSchema(**request.data).model_dump())

            return Response(status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class ManyBoidsFromDB(APIView):
    def __init__(self) -> None:
        super().__init__()
        # self.db = GSGenericORM(GS_SPREADSHEET, GS_WORKSHEET, id_column="user_id")

    def get(self, request):
        # boids = self.db.all()
        boids = firebase_db.collection("boids").stream()
        json_boids = {boid.id: boid.to_dict() for boid in boids}
        return JsonResponse(json_boids)

    def post(self, request):
        try:

            if not request.data:
                return Response(
                    {"error": "No data provided. Please include the required fields."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            request_data: BoidSchema = BoidSchema(**request.data.copy())

            _, ref = firebase_db.collection("boids").add(request_data.model_dump())

            return JsonResponse({"id": ref.id}, status=status.HTTP_201_CREATED)

        except ValueError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response(
                {"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ManyBoidsFromSimulation(APIView):

    def get(self, request):

        with data_lock:
            boids = {
                boid_id: boid.to_dict() for boid_id, boid in BOID_DICT.copy().items()
            }

        return JsonResponse(boids)


class SingleBoidFromSimulation(APIView):

    def get(self, request, pk):

        print(pk)

        with data_lock:
            boids = {boid_id: boid.to_dict() for boid_id, boid in BOID_DICT.items()}

            boid = boids.get(pk, {})

        return JsonResponse(boid)
