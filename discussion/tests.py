import time
from django.test import TestCase
import json
from rest_framework.test import APITestCase, APIClient, RequestsClient
import pytest
from rest_framework import status
from seniorProjectBackendDjango.db import GS_DiscussionSchema

BASE_URL = "http://127.0.0.1:8000/discussion_service"

class DBViewsTests(APITestCase):

    def setUp(self):
        time.sleep(5)

    def test_get_discussions(self):
        res = self.client.get(BASE_URL + "/discussions/")

        self.assertIsNot(res.json(), {}, "Got empty JSON, expected result")
        self.assertEqual(res.status_code, status.HTTP_200_OK, f"Got response status: {res.status_code}")
        self.assertGreaterEqual(len(res.json()), 0)

    def test_get_existing_discussion_by_id(self):
        res = self.client.get(BASE_URL + "/discussions/250c8715-1d5c-5bcc-b015-799834/")

        self.assertIsNot(res.json(), {}, "Got empty JSON, expected result")
        self.assertEqual(res.status_code, status.HTTP_200_OK, f"Got response status: {res.status_code}")

    def test_get_nonexisting_discussion_by_id(self):
        res = self.client.get(BASE_URL + "/discussions/9999/")
        self.assertEqual(res.json(), {"message": "Couldn't get discussion from db - Status: False"})

    def test_get_nonint_discussion_by_id(self):
        res = self.client.get(BASE_URL + "/discussions/hey_mom/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, f"Got response status: {res.status_code}")
    
    def test_post_discussion(self):
        post_data: GS_DiscussionSchema = {
            "user_id": "250c8715-1d5c-5bcc-b015-799834",
            "title": "I don't speak German neither...",
            "body": "Can someone please teach me?",
        }
        res = self.client.post(BASE_URL + "/discussions/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, f"Didn't create, status code {res.status_code}")

    def test_post_with_no_data(self):

        res = self.client.post(BASE_URL + "/discussions/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't update, status code {res.status_code}")

    def test_post_invalid_discussion(self):
        post_data: GS_DiscussionSchema = {
            "user_id": "250c8715-1d5c-5bcc-b015-799834",
            "title": "I don't speak German neither...",
            "updated_at": "12/14/2024"
        }
        res = self.client.post(BASE_URL + "/discussions/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't throw proper error, status code {res.status_code}")
    
    def test_delete_discussion(self):

        post_data: GS_DiscussionSchema = {
            "user_id": "20544c72-ce5a-7505-167f-dc8906",
            "title": "I don't speak German neither...",
            "body": "Can someone please teach me?",
        }

        res = self.client.post(BASE_URL + "/discussions/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, f"Didn't create, status code {res.status_code}")
        discussion_id = res.json().get("discussion_id")

        res = self.client.delete(BASE_URL + f"/discussions/{discussion_id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, f"Didn't delete, status code {res.status_code}")
    
    def test_delete_nonexistent_boid(self):

        res = self.client.delete(BASE_URL + "/discussions/9999/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't delete, status code {res.status_code}")

    def test_update_discussion(self):

        post_data: GS_DiscussionSchema = {
            "user_id": "20544c72-ce5a-7505-167f-dc8906",
            "title": "I don't speak German neither...",
            "body": "Can someone please teach me?",
        }
        res = self.client.post(BASE_URL + "/discussions/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, f"Didn't create, status code {res.status_code}")

        discussion_id = res.json().get("discussion_id")

        patch_data: GS_DiscussionSchema = {
            "user_id": "20544c72-ce5a-7505-167f-dc8906",
            "discussion_id": discussion_id,
            "title": "You eat babies!",
            "body": "Said John to the nice monster man",
            "created_at": "12/14/2024",
            "updated_at": "12/14/2024"
        }

        res = self.client.patch(BASE_URL + f"/discussions/{discussion_id}/", json.dumps(patch_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK, f"Didn't update, status code {res.status_code}")
    
    def test_update_nonexistent_discussion_with_data(self):
        patch_data: GS_DiscussionSchema = {
            "user_id": 4,
            "discussion_id": 9999,
            "title": "C'mon Black Lung...",
            "body": "I've gotta go meet with Dutch",
            "created_at": "12/14/2024",
            "updated_at": "12/14/2024"
        }

        res = self.client.patch(BASE_URL + "/discussions/9999/", json.dumps(patch_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't update, status code {res.status_code}")

    def test_update_with_no_data(self):

        res = self.client.patch(BASE_URL + "/discussions/9999/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Didn't update, status code {res.status_code}")

    def test_validate_wrong_type(self):
        post_data: GS_DiscussionSchema = {
            "user_id": 4,
            "title": 98,
            "body": True,
        }

        res = self.client.post(BASE_URL + "/discussions/", json.dumps(post_data), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Supposed to NOT work, status code {res.status_code}")