from django.urls import path
from django.urls import include
from .views import *

urlpatterns = [
    path('login/', spotify_login),
    path('callback/', spotify_callback),
    path('getsummary/', get_spotify_summary),
    path('checkloggedin/', checkloggedin),
    path('debug/', get_spotify_summary),
]