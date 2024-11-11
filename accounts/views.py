from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from .models import UserSpotifyData

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email is already taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'You are now registered and can log in')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'accounts/register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    user_data_list = []
    if request.user.is_authenticated:
        user_data_list = UserSpotifyData.objects.filter(user=request.user)
    return render(request, 'accounts/dashboard.html', {'user_data_list': user_data_list})


@login_required(login_url='login')
def delete_account(request):
    user = request.user
    user.delete()  # Delete the user account
    logout(request)  # Log the user out
    messages.success(request, 'Your account has been deleted successfully.')
    return redirect('login')

def spotify_login(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-top-read"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def spotify_callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-top-read"
    )
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    # Save access_token to user session
    request.session['spotify_access_token'] = access_token

    sp = spotipy.Spotify(auth=access_token)
    user_top_tracks = sp.current_user_top_tracks(limit=10)  # Example: Get user's top 10 tracks

    if request.user.is_authenticated:
        wrap_name = f"Spotify Wrap {UserSpotifyData.objects.filter(user=request.user).count() + 1}"
        user_data = UserSpotifyData.objects.create(
            user=request.user,
            wrap_name=wrap_name,
            top_tracks=user_top_tracks
        )
        user_data.save()

    return redirect('dashboard')

    # Pass user statistics to the template
    #return render(request, 'accounts/dashboard.html', {'user_top_tracks': user_top_tracks})

    #return redirect('dashboard')  # Redirect to dashboard or any other page