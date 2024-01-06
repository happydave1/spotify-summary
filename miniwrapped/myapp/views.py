from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from dotenv import load_dotenv
import os
import requests
from base64 import b64encode
from urllib.parse import urlencode

# Create your views here.

# test function
def main(request):
    return HttpResponse("hello from django!")


# Use spotipy's OAuth2 module to redirect users to Spotify's authentication
def spotify_login(request):

    # DEBUG
    print('entered spotify_login')

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
        scope='user-library-read user-read-playback-state user-modify-playback-state user-top-read',
    )

    try:
        # get Spotify's authentication url
        auth_url = sp_oauth.get_authorize_url()

        # DEBUG
        print("got the auth_url! going to redirect to spotify")
        print(auth_url)

        return redirect(auth_url)
    except Exception as e:
        # Handle any exceptions that might occur
        print(f"Error during Spotify authentication: {e}")


# Handle callback & get access token
def spotify_callback(request):

    # DEBUG
    print('entered spotify_callback')

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
        scope='user-library-read user-read-playback-state offline_access',
    )

    print("created sp_oauth")

    code = request.GET.get('code', None)

    # get token & store it
    
    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'data': {
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        },
        'headers': {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        }
    }

    # store token
    response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])
    response_info = response.json()
    access_token = response_info.get('access_token')
    refresh_token = response_info.get('refresh_token')

    # DEBUG CODE TO CHECK IF THE TOKENS WORK
    check = checkExpired(access_token=access_token, refresh_token=refresh_token)
    print(check)


    # redirect back to frontend
    redirect_url = 'http://localhost:3000/'

    # create payload
    data = {
        'access_token' : access_token,
        'refresh-token' : refresh_token,
    }

    # Append data to the redirect URL as query parameters
    query_parameters = '&'.join([f"{key}={value}" for key, value in data.items()])
    final_redirect_url = f"{redirect_url}?{query_parameters}"

    # Frontend will have access to access token and refresh token
    return redirect(final_redirect_url)

# Get summary of listened songs
def get_spotify_summary(request):

    # get token info from session
    stored_token_info = request.session.get('spotify_token_info')

    # check if it exists
    if stored_token_info:

        print("stored token info exists")

        access_token = stored_token_info['access_token']
        
        url = 'https://api.spotify.com/v1/me/top/artists'

        headers = {
            'Authorization': 'Bearer ' + access_token,  # Replace with your actual access token
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # Successful request
            data = response.json()
            # Return data
            return JsonResponse(data)
        else:
            
            # try refreshing token
            CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
            CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
            refresh_token = stored_token_info.get('refresh_token')
            print(refresh_token)
            new_access_token = refresh_access_token(CLIENT_ID, CLIENT_SECRET, refresh_token)
            new_header = {
                'Authorization': 'Bearer ' + new_access_token,
            }
            new_response = requests.get(url, headers=new_header)
            if (new_response.status_code == 200):
                print("successful!")

            # Error handling
            print(f"HTTP Error {response.status_code}: {response.text}")
            return HttpResponse("Error while checking top artists!")



# Function to check if a user has logged in yet
def checkloggedin(request):

    spotify_token_info = request.session.get('spotify_token_info')
    print(spotify_token_info)

    if (spotify_token_info == None):
        return JsonResponse(
            { 'result': False }
        )
    
    access_token = spotify_token_info.get('access_token')
    refresh_token = spotify_token_info.get('refresh_token')

    check = checkExpired(access_token=access_token, refresh_token=refresh_token)


    if (not check):
        
        # access token is expired
        load_dotenv()
        CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
        request.session['access_token'] = refresh_token(CLIENT_ID, refresh_token)

        # got new access token -> try checkExpired again
        new_check = checkExpired(request.session.get('access_token'), refresh_token=refresh_token)
        
        # returns
        if (new_check):
            return JsonResponse(
                { 'result': True }
            )
        
        return JsonResponse(
            { 'result': False }
        )

    # access token works -> return Json success
    return JsonResponse(
        { 'result': True }
    )


def refresh_access_token(client_id, refresh_token):
    """
    Function to refresh an access token from Spotify.

    :param client_id: str representing client id
    :param refresh_token: str representing refresh token
    :return: str representing new access token and optionally new refresh token
    """

    url = "https://accounts.spotify.com/api/token"

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        # Make a POST request to the token endpoint
        response = requests.post(url, data=payload, headers=headers)

        # Parse the JSON response
        response_data = response.json()

        # Check for errors in the response
        if 'error' in response_data:
            print(f"Error refreshing access token: {response_data['error']}")
            return None

        # Extract the new access token from the response
        new_access_token = response_data['access_token']

        # Optionally, extract and store a new refresh token
        new_refresh_token = response_data.get('refresh_token')

        # Print or return the new access token
        print(f"New Access Token: {new_access_token}")

        # Return the new access token (and optionally the new refresh token)
        return new_access_token, new_refresh_token

    except Exception as e:
        print(f"Error during token refresh: {e}")
        return None
    


def checkExpired(access_token, refresh_token):

    # check if there is an access_token
    # if there isnt -> return false
    if (access_token == None or refresh_token == None):
        return False
    
    print('there is token info')
    
    # check if access token works
    try:
        
        # use Spotipy to check
        sp = spotipy.Spotify(access_token)
        top_tracks = sp.current_user_top_tracks(time_range='short_term', limit=10)

        # if code gets to this line -> access token works
        print('access token works')
        return True


    except Exception as e:

        # access token does not work -> use refresh token to get new access token
        print('access token does not work')

        return False
        