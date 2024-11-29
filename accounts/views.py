from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import urllib.parse
import requests
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
    """Display user's dashboard with Spotify wraps."""
    # Fetch all previously stored wraps for the user
    user_data_list = UserSpotifyData.objects.filter(user=request.user)

    # Show wraps if they exist
    return render(request, 'accounts/dashboard.html', {'user_data_list': user_data_list})

    # user_data_list = []
    # if request.user.is_authenticated:
    #     access_token = request.session.get('spotify_access_token')
    #     if access_token:
    #         top_tracks = get_user_top_tracks(access_token)

    #         # Save data if needed
    #         user_data = UserSpotifyData.objects.create(
    #             user=request.user,
    #             wrap_name="Latest Wrap",
    #             top_tracks=top_tracks,
    #         )
    #         user_data_list = UserSpotifyData.objects.filter(user=request.user)

    # return render(request, 'accounts/dashboard.html', {'user_data_list': user_data_list})

@login_required(login_url='login')
def delete_account(request):
    user = request.user
    user.delete()  # Delete the user account
    logout(request)  # Log the user out
    messages.success(request, 'Your account has been deleted successfully.')
    return redirect('login')

@login_required
def spotify_login(request):
    #requests.session.pop('spotify_access_token', None)
    # print("Clearing session...")
    # request.session.flush()
    # print("Session cleared.")
    # if 'spotify_access_token' in request.session:
    #     del request.session['spotify_access_token']

    base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": "user-top-read",
        "show_dialog": "true",
    }
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

def spotify_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('dashboard')
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()
    access_token = response_data.get('access_token')

    # Save access token to the session
    request.session['spotify_access_token'] = access_token
    # if request.user.is_authenticated:
    #     top_tracks = get_user_top_tracks(access_token)
    #     if top_tracks:
    #         wrap_name = f"Spotify Wrap {UserSpotifyData.objects.filter(user=request.user).count() + 1}"
    #         UserSpotifyData.objects.create(
    #             user=request.user,
    #             wrap_name=wrap_name,
    #             top_tracks=top_tracks,
    #         )

    return redirect('dashboard')
    # Pass user statistics to the template
    #return render(request, 'accounts/dashboard.html', {'user_top_tracks': user_top_tracks})

    #return redirect('dashboard')  # Redirect to dashboard or any other page

def create_wrapped(request):
    # # Check if the user is logged in with Spotify
    # access_token = request.session.get('spotify_access_token')
    # if not access_token:
    #     return JsonResponse({'error': 'Log in with Spotify first'}, status=401)

    # # Check if a wrap already exists for the current user
    # existing_wraps = UserSpotifyData.objects.filter(user=request.user)
    # if existing_wraps.exists():
    #     return JsonResponse({'warning': 'You already have a wrap created for this session.'}, status=200)

    # # If no wraps exist, create a new one
    # user_top_tracks = get_user_top_tracks(access_token)  # Fetch top tracks from Spotify
    # if user_top_tracks:
    #     wrap_name = f"Spotify Wrap {existing_wraps.count() + 1}"
    #     UserSpotifyData.objects.create(
    #         user=request.user,
    #         wrap_name=wrap_name,
    #         top_tracks=user_top_tracks
    #     )
    #     return JsonResponse({'success': 'New wrapped created successfully'})

    # return JsonResponse({'error': 'Failed to fetch Spotify data'}, status=400)

    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return JsonResponse({'error': 'Log in with Spotify first'}, status=401)

    force_create = request.GET.get('force', 'false').lower() == 'true'

    existing_wraps = UserSpotifyData.objects.filter(user=request.user)
    if existing_wraps.exists() and not force_create:
        return JsonResponse({'warning': 'You already have a wrap created for this session.'}, status=200)

    # Generate new wrapped
    user_top_tracks = get_user_top_tracks(access_token)  # Fetch top tracks from Spotify
    if user_top_tracks:
        wrap_name = f"Spotify Wrap {UserSpotifyData.objects.filter(user=request.user).count() + 1}"
        UserSpotifyData.objects.create(
            user=request.user,
            wrap_name=wrap_name,
            top_tracks=user_top_tracks
        )
        return JsonResponse({'success': 'New wrapped created successfully'})

    return JsonResponse({'error': 'Failed to fetch Spotify data'}, status=400)



def get_user_top_tracks(access_token):
    api_url = "https://api.spotify.com/v1/me/top/tracks?limit=10"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(api_url, headers=headers)
    return response.json()

