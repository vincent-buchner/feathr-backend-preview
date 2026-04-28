import datetime
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from seniorProjectBackendDjango.db import GS_DiscussionSchema, GSGenericORM
from rest_framework import status
import os

GS_SPREADSHEET = os.getenv("GS_SPREADSHEET")
GS_WORKSHEET_DISCUSSION = "Discussion"


class SingleDiscussionFromDB(APIView):
    def __init__(self) -> None:
        super().__init__()
        self.db = GSGenericORM(GS_SPREADSHEET, GS_WORKSHEET_DISCUSSION, id_column="discussion_id")

    def get(self, request, pk):
        success, discussion = self.db.get_by_id(pk)

        if success and discussion:
            return JsonResponse(discussion)
        else:
            return JsonResponse(
                {"message": f"Couldn't get discussion from db - Status: {success}"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            success, message = self.db.delete(pk)
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

            success = self.db.update(pk, request.data)
            if not success:
                raise KeyError(f"Couldn't update db entry")
            
            return Response(status=status.HTTP_200_OK)
        except KeyError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class ManyDiscussionsFromDB(APIView):
    def __init__(self) -> None:
        super().__init__()
        self.db = GSGenericORM(GS_SPREADSHEET, GS_WORKSHEET_DISCUSSION, id_column="discussion_id")

    def get(self, request):
        discussions = self.db.all()
        return JsonResponse(discussions, safe=False)

    def post(self, request):
        try:
            if not request.data:
                return Response(
                    {"error": "No data provided. Please include the required fields."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            discussion_id = str(uuid.uuid4())

            request_data: GS_DiscussionSchema = request.data.copy()

            request_data["created_at"] = datetime.datetime.today().strftime("%m-%d-%Y")
            request_data["updated_at"] = datetime.datetime.today().strftime("%m-%d-%Y")
            request_data["discussion_id"] = discussion_id

            success, message = self.db.insert(GS_DiscussionSchema.validate(request_data))
            if not success:
                return Response({"error": f"Couldn't create db entry: {message}"})
            
            return Response(status=status.HTTP_201_CREATED, data={"discussion_id": discussion_id})
        except ValueError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

