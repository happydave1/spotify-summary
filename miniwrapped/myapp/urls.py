from django.urls import path, re_path
from django.urls import include
from .views import *

urlpatterns = [
    path('login/', spotify_login),
    path('callback/', spotify_callback),
    path('getsummary/', get_spotify_summary),
    path('checkloggedin/', checkloggedin),
    path('checkloggedin/&access_token=<str:access_token>&refresh_token=<str:refresh_token>', checkloggedin),
    path('debug/', get_spotify_summary),
]