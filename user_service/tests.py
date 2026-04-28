import time
import json
from rest_framework.test import APITestCase, APIClient, RequestsClient
import pytest
from rest_framework import status
from seniorProjectBackendDjango.db import GS_UserSchema

BASE_URL = "http://127.0.0.1:8000/user_service"

class UserTests(APITestCase):

    def setUp(self):
        time.sleep(5)

    def test_get_users(self):

        res = self.client.get(BASE_URL + "/users/")

        self.assertIsNot(res.json(), {}, "Got empty JSON, expected result")
        self.assertEqual(res.status_code, status.HTTP_200_OK, f"Got response status: {res.status_code}")
        self.assertGreaterEqual(len(res.json()), 0)

    def test_get_existing_user_by_id(self):
        res = self.client.get(BASE_URL + "/users/20544c72-ce5a-7505-167f-dc8906/")

        self.assertIsNot(res.json(), {}, "Got empty JSON, expected result")
        self.assertEqual(res.status_code, status.HTTP_200_OK, f"Got response status: {res.status_code}")

    def test_get_nonexisting_user_by_id(self):
        res = self.client.get(BASE_URL + "/users/9999/")
        self.assertEqual(res.json(), {"message": "Couldn't get user from db - Status: False"})

    def test_get_nonint_user_by_id(self):
        res = self.client.get(BASE_URL + "/users/hey_mom/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, f"Got response status: {res.status_code}")

    def test_post_user(self):
        post_data: GS_UserSchema = {
            "user_name": "Lillian Powell",
            "email": "lillian.powell@van-der-linde.com",
            "profile_picture": "https://images.dog.ceo/breeds/boxer/n02108089_5423.jpg",
            "location": "Emerald Ranch",
            "gender": "Female",
        }

        res = self.client.post(BASE_URL + "/users/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, f"Didn't create, status code {res.status_code}")

    def test_post_with_no_data(self):

        res = self.client.post(BASE_URL + "/users/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't update, status code {res.status_code}")

    def test_post_invalid_user(self):
        post_data: GS_UserSchema = {
            "email": "lillian.powell@van-der-linde.com",
        }

        res = self.client.post(BASE_URL + "/users/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't throw proper error, status code {res.status_code}")

    def test_delete_user(self):

        post_data: GS_UserSchema = {
            "user_name": "Lillian Powell",
            "email": "lillian.powell@van-der-linde.com",
            "profile_picture": "https://images.dog.ceo/breeds/boxer/n02108089_5423.jpg",
            "location": "Emerald Ranch",
            "gender": "Female",
        }

        res = self.client.post(BASE_URL + "/users/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, f"Didn't create, status code {res.status_code}")

        res = self.client.delete(BASE_URL + f"/users/{res.json().get("user_id")}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, f"Didn't delete, status code {res.status_code}")

    def test_delete_nonexistent_boid(self):

        res = self.client.delete(BASE_URL + "/users/9999/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't delete, status code {res.status_code}")

    def test_update_user(self):

        post_data: GS_UserSchema = {
            "user_name": "Lillian Powell",
            "email": "lillian.powell@van-der-linde.com",
            "profile_picture": "https://images.dog.ceo/breeds/boxer/n02108089_5423.jpg",
            "location": "Emerald Ranch",
            "gender": "Female",
        }

        res = self.client.post(BASE_URL + "/users/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, f"Didn't create, status code {res.status_code}")
        user_id = res.json().get("user_id")
        boid_id = res.json().get("boid_id")

        patch_data: GS_UserSchema = {
            "user_id": user_id,
            "user_name": "Ezekiel Harper",
            "email": "ezekiel.harper@van-der-linde.com",
            "profile_picture": "https://example.com/images/ezekiel_harper.jpg",
            "location": "Butcher Creek",
            "gender": "Male",
            "date_joined": "1899-06-03",
            "updated_at": "1899-06-15",
            "boid_id": boid_id,
        }

        res = self.client.patch(BASE_URL + f"/users/{user_id}/", json.dumps(patch_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK, f"Didn't update, status code {res.status_code}")

    def test_update_nonexistent_user_with_data(self):
        patch_data: GS_UserSchema = {
            "user_id": 9999,
            "user_name": "Uncle",
            "email": "uncle@van-der-linde.com",
            "profile_picture": "https://example.com/images/uncle.jpg",
            "location": "Camp",
            "gender": "Male",
            "date_joined": "1899-06-03",
            "updated_at": "1899-06-15",
            "boid_id": 11,
        }

        res = self.client.patch(BASE_URL + "/users/9999/", json.dumps(patch_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't update, status code {res.status_code}")

    def test_update_with_no_data(self):

        res = self.client.patch(BASE_URL + "/users/9999/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't update, status code {res.status_code}")

    def test_validate_wrong_type(self):
        post_data: GS_UserSchema = {
            "user_name": True,
            "email": "uncle@van-der-linde.com",
            "profile_picture": True,
            "location": 98,
            "gender": "Male",
        }

        res = self.client.post(BASE_URL + "/users/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Supposed to NOT work, status code {res.status_code}")
