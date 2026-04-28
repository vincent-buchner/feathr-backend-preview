from django.urls import path
from . import views

urlpatterns = [
    path('', views.SaySomethingView.as_view())
]