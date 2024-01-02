from django.urls import path
from django.urls import include
from .views import main, spotify_login, spotify_callback

urlpatterns = [
    path('test/', spotify_login),
    path('callback/', spotify_callback),
]