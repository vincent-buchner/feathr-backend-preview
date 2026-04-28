from django.urls import path
from .views import ManyDiscussionsFromDB, SingleDiscussionFromDB

urlpatterns = [
    path('discussions/', ManyDiscussionsFromDB.as_view(), name='many_discussions'),  # Matches GET /discussions/
    path('discussions/<str:pk>/', SingleDiscussionFromDB.as_view(), name='single_discussion'),  # Matches GET/POST/DELETE /discussions/<id>/
]

