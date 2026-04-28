import time
from unittest import mock
from unittest.mock import MagicMock, patch
import uuid
from google.cloud import firestore
from firebase_admin import auth
# import threading
from django.test import TestCase
import json
from rest_framework.test import APITestCase, APIClient, RequestsClient
import pytest
from rest_framework import status
# from boidsSimulation.simulation.run import data_lock
from boidsSimulation.views import CreateOrQueryUserBoid
from seniorProjectBackendDjango.db import BoidSchema

SIM_BOIDS_URL = "http://127.0.0.1:8000/boids-service/simulation_boids/"
DB_BOIDS_URL = "http://127.0.0.1:8000/boids-service/db_boids/"
BASE_URL = "http://127.0.0.1:8000/boids_service"


class DBViewsTests(APITestCase):

    def setUp(self):
        time.sleep(1)

    def test_get_existing_boid_by_id(self):
        res = self.client.get(BASE_URL + "/db_boids/zlFNLWWyOTE46xYEN6Zz/")

        self.assertIsNot(res.json(), {}, "Got empty JSON, expected result")
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            f"Got response status: {res.status_code}",
        )

    def test_get_nonexisting_boid_by_id(self):
        res = self.client.get(BASE_URL + "/db_boids/9999/")
        self.assertContains(res, "message")

    # def test_post_boid(self):
    #     print("Posting boid...")
    #     post_data: GS_BoidSchema = {
    #         "user_id": "24b5175a-9727-e33e-36b8-9146ab",
    #         "username": "Sadie Adler",
    #         "color": "#FFFFFF",
    #         "acceleration_x": 23,
    #         "acceleration_y": 23,
    #         "position_x": 18,
    #         "position_y": 18,
    #         "velocity_x": 45,
    #         "velocity_y": 45

    #     }
    #     res = self.client.post(BASE_URL + "/db_boids/", json.dumps(post_data), content_type="application/json")
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED, f"Didn't create, status code {res.status_code}")

    def test_post_with_no_data(self):

        res = self.client.post(BASE_URL + "/db_boids/")
        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
            f"Didn't update, status code {res.status_code}",
        )

    def test_post_invalid_boid(self):

        post_data = {"position_x": 4}

        res = self.client.post(
            BASE_URL + "/db_boids/",
            json.dumps(post_data),
            content_type="application/json",
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
            f"Didn't throw proper error, status code {res.status_code}",
        )

    def test_post_update_delete_boid(self):

        user_id = str(uuid.uuid4())

        post_data = BoidSchema(
            user_id=user_id,
            color="#FFFFFF",
            position_x=2,
            position_y=3,
            velocity_x=3,
            velocity_y=4,
        )

        patch_data = BoidSchema(
            user_id=user_id,
            color="#abcdef",
            position_x=5,
            position_y=3,
            velocity_x=200,
            velocity_y=4,
        )
        res = self.client.post(
            BASE_URL + "/db_boids/",
            post_data.model_dump_json(),
            content_type="application/json",
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
            f"Didn't create, status code {res.status_code}",
        )
        post_boid_id = res.json()["id"]
        res = self.client.patch(
            BASE_URL + f"/db_boids/{post_boid_id}/",
            patch_data.model_dump_json(),
            content_type="application/json",
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            f"Didn't update, status code {res.status_code}",
        )
        res = self.client.delete(BASE_URL + f"/db_boids/{post_boid_id}/")
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            f"Didn't delete, status code {res.status_code}",
        )

    def test_delete_nonexistent_boid(self):

        res = self.client.delete(BASE_URL + "/db_boids/9999/")
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            f"Didn't delete, status code {res.status_code}",
        )

    def test_update_nonexistent_boid_with_data(self):
        patch_data = BoidSchema(
            user_id="heyyyyyy",
            color="#abcdef",
            position_x=5,
            position_y=3,
            velocity_x=200,
            velocity_y=4,
        )

        res = self.client.patch(
            BASE_URL + "/db_boids/9999/",
            patch_data.model_dump_json(),
            content_type="application/json",
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
            f"Didn't update, status code {res.status_code}",
        )
        # self.assertEqual(res.json(), {"error": "Couldn't update db entry"})

    def test_update_with_no_data(self):

        res = self.client.patch(BASE_URL + "/db_boids/9999/")
        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
            f"Didn't update, status code {res.status_code}",
        )

    def test_get_all(self):
        res = self.client.get(BASE_URL + "/db_boids/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.json()), 0)


class SimulationViewTests(APITestCase):

    def test_get_config(self):
        res = self.client.get(BASE_URL + "/config/")

        self.assertContains(res, "WORLD_HEIGHT")
        self.assertContains(res, "WORLD_WIDTH")
        self.assertIsInstance(res.json()["WORLD_HEIGHT"], int | float)

    def test_get_all_boids_from_simulation(self):
        res = self.client.get(BASE_URL + "/simulation_boids/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(res.json().get("zlFNLWWyOTE46xYEN6Zz"), {})
        self.assertGreaterEqual(len(res.json()), 1)

    def test_get_single_boid_from_simulation(self):
        res = self.client.get(BASE_URL + "/simulation_boids/zlFNLWWyOTE46xYEN6Zz/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(res.json(), {})

class CreateOrQueryUserBoidTests(APITestCase):

    @patch('firebase_admin.auth.get_user')
    @patch('firebase_admin.auth.verify_id_token')
    def test_new_user_new_boid(self, mock_verify_id_token, mock_get_user):

        # Mock the Firebase auth calls
        mock_verify_id_token.return_value = {'uid': 'I am a test'}

        # Mock the auth user call
        mock_user = MagicMock()
        mock_user.display_name = "Arthur Morgan"
        mock_get_user.return_value = mock_user

        # Make the POST request
        res = self.client.post(
            BASE_URL + "/create_user_boid/",  # Just the path since BASE_URL is handled by test client
            data=json.dumps({
                "user_id": "I am a test",
                "id_token": "I am a test too"
            }),
            content_type="application/json",
        )

        # Assert response
        self.assertEqual(res.status_code, 200)
        parsed_res = CreateOrQueryUserBoid.UserBoidResponse(**res.json())
        
        self.assertEqual(parsed_res.errors, [])
        self.assertNotEqual(parsed_res.boid_id, "")
        self.assertEqual(parsed_res.message, "Created new user boid")
        
        boid_id = res.json().get("boid_id")

        res = self.client.delete(BASE_URL + f"/db_boids/{boid_id}/")
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            f"Didn't delete, status code {res.status_code}",
        )

    def tearDown(self):
        # Clean up Firestore client if initialized
        from google.cloud.firestore import Client
        if hasattr(firestore, '_client') and firestore._client is not None:
            firestore._client.close()  # Close the Firestore client explicitly
        
        # Clear any Firebase app instances if initialized
        from firebase_admin import delete_app, get_app
        try:
            delete_app(get_app())
        except ValueError:
            pass  # No app to delete
