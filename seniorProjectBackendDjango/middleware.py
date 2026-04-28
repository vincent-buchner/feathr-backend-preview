from django.http import JsonResponse
from django.conf import settings
from django.urls import resolve
import requests
import os
from rest_framework.exceptions import AuthenticationFailed

PROTECTED_ROUTES = {
    "auth_single_db_boid": ["DELETE", "PATCH"],
    "auth_many_db_boids": ["POST"],
    "many_discussions": ["GET", "POST"],
    "single_discussions": ["GET", "PATCH", "DELETE"],
    "many_users": ["GET", "PATCH", "DELETE"],
    "single_users": ["GET", "POST"]
}

class ProtectedRouteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # If we aren't in production, just continue
        if getattr(settings, 'TESTING', False):
            return self.get_response(request)

        # Get the current view name
        resolver_match = resolve(request.path_info)
        view_name = resolver_match.view_name

        protected_methods = PROTECTED_ROUTES.get(view_name, [])
        if request.method in protected_methods:

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JsonResponse({"error": "Authorization header missing"}, status=401)
    
            access_token = auth_header.split("Bearer ")[1]

            GOOGLE_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"
            GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

            response = requests.get(GOOGLE_TOKEN_INFO_URL, params={"access_token": access_token})

            if response.status_code != 200:
                return JsonResponse({"error": "Invalid or expired access token"})

            token_info = response.json()

            if token_info.get("aud") != GOOGLE_CLIENT_ID:
                return JsonResponse({"error": "Invalid token audience"})
            
            request.user_info = {
                "email": token_info.get("email", ""),
                "name": token_info.get("name", ""),
                "picture": token_info.get("picture", ""),
            }

        return self.get_response(request)
