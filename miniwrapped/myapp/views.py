from django.shortcuts import render, redirect
from django.http import HttpResponse
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Create your views here.

# test function
def main(request):
    return HttpResponse("hello from django!")


# Use spotipy's OAuth2 module to redirect users to Spotify's authentication
def spotify_login(request):

    # load .env
    load_dotenv()

    # store environment variables from .env
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

    # create SpotifyOAuth object -> used for authentication
    sp_oauth = SpotifyOAuth(
        CLIENT_ID,
        CLIENT_SECRET,
        REDIRECT_URI,
        scope='user-library-read user-read-playback-state user-modify-playback-state',
    )

    # get Spotify's authentication url
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


# Handle callback & get access token
def spotify_callback(request):

    # load .env
    load_dotenv()

    # store environment variables from .env
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

    # create SpotifyOAuth object -> used for authentication
    sp_oauth = SpotifyOAuth(
        CLIENT_ID,
        CLIENT_SECRET,
        REDIRECT_URI,
        scope='user-library-read user-read-playback-state user-modify-playback-state',
    )

    # get token & store it
    token_info = sp_oauth.get_access_token(request.GET['code'])
    request.session['spotify_token_info'] = token_info

    # TODO: get user recently listened to


    # redirect back to frontend
    return redirect('http://localhost:3000/')