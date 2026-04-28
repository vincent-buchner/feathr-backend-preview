from django.urls import path
from .views import SingleUser, ManyUsers

urlpatterns = [
    path('users/', ManyUsers.as_view(), name='many_users'),  # Matches GET /users/
    path('users/<str:pk>/', SingleUser.as_view(), name='single_user'),  # Matches GET/POST/DELETE /users/<id>/
]