from django.urls import path
from boidsSimulation import views

urlpatterns = [
    path('db_boids_auth/<str:pk>/', views.SingleBoidFromDB.as_view(), name="auth_single_db_boid"), # Protect
    path('db_boids_auth/', views.ManyBoidsFromDB.as_view(), name="auth_many_db_boids"), # Protect
    path('db_boids/<str:pk>/', views.SingleBoidFromDB.as_view()), # UnProtect
    path('db_boids/', views.ManyBoidsFromDB.as_view()), # UnProtect
    path('create_user_boid/', views.CreateOrQueryUserBoid.as_view()), # UnProtect
    path('simulation_boids/', views.ManyBoidsFromSimulation.as_view()),
    path('simulation_boids/<str:pk>/', views.SingleBoidFromSimulation.as_view()),
    path('config/', views.simulation_config)
]