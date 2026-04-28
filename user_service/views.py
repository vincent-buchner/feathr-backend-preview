import datetime
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from seniorProjectBackendDjango.db import GS_UserSchema, GSGenericORM
from rest_framework import status
import os

from user_service.utils import isEmail

GS_SPREADSHEET = os.getenv("GS_SPREADSHEET")
GS_WORKSHEET_DISCUSSION = "User"

class SingleUser(APIView):
    def __init__(self) -> None:
        super().__init__()

        # Fetching single users by their user_id or email
        self.db_user_id = GSGenericORM(GS_SPREADSHEET, GS_WORKSHEET_DISCUSSION, id_column="user_id")
        self.db_email = GSGenericORM(GS_SPREADSHEET, GS_WORKSHEET_DISCUSSION, id_column="email")

    def determine_database_instance(self, pk: str) -> GSGenericORM:
        return self.db_email if isEmail(pk) else self.db_user_id

    def get(self, request, pk):
        db = self.determine_database_instance(pk)
        success, discussion = db.get_by_id(pk)

        if success and discussion:
            return JsonResponse(discussion)
        else:
            return JsonResponse(
                {"message": f"Couldn't get user from db - Status: {success}"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            db = self.determine_database_instance(pk)
            success, message = db.delete(pk)
            if not success:
                raise KeyError(f"Couldn't delete db entry: {message}")
            return Response(status=status.HTTP_200_OK)
        except KeyError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            if not request.data:
                return Response(
                    {"error": "No data provided. Please include the required fields."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            db = self.determine_database_instance(pk)

            success = db.update(pk, request.data)
            if not success:
                raise KeyError(f"Couldn't update db entry")
            
            return Response(status=status.HTTP_200_OK)
        except KeyError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class ManyUsers(APIView):
    def __init__(self) -> None:
        super().__init__()
        self.db = GSGenericORM(GS_SPREADSHEET, GS_WORKSHEET_DISCUSSION, id_column="user_id")

    def get(self, request):
        discussions = self.db.all()
        return JsonResponse(discussions, safe=False)

    def post(self, request):
        # TODO: From request: username, email, pfp, location
        # TODO: Generate: user_id, date_joined, updated_at, boid_id (from creating boid)
        try:

            # If there's no request data, return 400
            if not request.data:
                return Response(
                    {"error": "No data provided. Please include the required fields."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add the needed generated values from the request: user_id, date_joined, updated_at, and boid_id
            # Let's create a user id and boid id 
            user_id = str(uuid.uuid4())
            boid_id = str(uuid.uuid4())

            # Now create a copy of the request and generate fields
            request_data: GS_UserSchema = request.data.copy()
            request_data["updated_at"] = datetime.date.today().strftime("%m-%d-%Y")
            request_data["date_joined"] = datetime.date.today().strftime("%m-%d-%Y")
            request_data["user_id"] = user_id
            request_data["boid_id"] = boid_id

            # Now create user, if not successful throw error
            success, message = self.db.insert(GS_UserSchema.validate(request_data))
            if not success:
                return Response({"error": f"Couldn't create db entry: {message}"})
            
            # Return the user_id and boid_id
            return Response(status=status.HTTP_201_CREATED, data={"user_id": user_id, "boid_id": boid_id})
        except ValueError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

