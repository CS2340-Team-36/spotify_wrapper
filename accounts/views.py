from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.conf import settings
import urllib.parse
import requests
from .models import UserSpotifyData
from django.views.decorators.cache import never_cache
import base64
from django.core.mail import send_mail


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

@login_required
def dashboard(request):
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        messages.error(request, "Spotify access token is missing. Please log in with Spotify again.")
        return redirect('spotify_login')

    # Fetch and display wraps
    user = request.user
    short_term_wraps = UserSpotifyData.objects.filter(user=user, term='short_term')
    medium_term_wraps = UserSpotifyData.objects.filter(user=user, term='medium_term')
    long_term_wraps = UserSpotifyData.objects.filter(user=user, term='long_term')

    return render(request, 'accounts/dashboard.html', {
        'short_term_wraps': short_term_wraps,
        'medium_term_wraps': medium_term_wraps,
        'long_term_wraps': long_term_wraps,
    })

@login_required(login_url='login')
def delete_account(request):
    user = request.user
    user.delete()  # Delete the user account
    logout(request)  # Log the user out
    messages.success(request, 'Your account has been deleted successfully.')
    return redirect('login')

@login_required
def spotify_login(request):
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
    """Handle Spotify's OAuth callback and exchange code for access token."""
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

    # Get access and refresh tokens
    access_token = response_data.get('access_token')
    refresh_token = response_data.get('refresh_token')  # May be None if not requested
    if not access_token:
        # Handle token retrieval failure
        return JsonResponse({'error': 'Failed to retrieve access token. Please try logging in again.'}, status=401)

    # Save tokens to session
    request.session['spotify_access_token'] = access_token
    if refresh_token:
        request.session['spotify_refresh_token'] = refresh_token



    return redirect('dashboard')  # Redirect to the dashboard after successful login


def refresh_access_token(refresh_token):
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,

# def get_user_top_tracks(access_token):
#     """Fetch user's top tracks from Spotify."""
#     api_url = "https://api.spotify.com/v1/me/top/tracks?limit=10"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

# @login_required
# def create_wrapped(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({'error': 'User not authenticated'}, status=401)
    
#     if request.method == 'POST':
#         # Step 1: Fetch Spotify data (replace with actual access token for authenticated user)
#         access_token = request.session.get('spotify_access_token')
#         refresh_token = request.session.get('spotify_refresh_token')  # Get the refresh token if available
#         if not access_token:
#             return JsonResponse({'error': 'No Spotify token found for the user. Please authenticate with Spotify.'}, status=401)

#         headers = {
#             'Authorization': f'Bearer {access_token}',
#         }

#         # Fetch top tracks and top artists (limit 10)
#         top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks?limit=10'
#         top_artists_url = 'https://api.spotify.com/v1/me/top/artists?limit=10'

#         # Step 2: Try fetching top tracks and top artists
#         top_tracks_response = requests.get(top_tracks_url, headers=headers)
#         top_artists_response = requests.get(top_artists_url, headers=headers)

#         # Check for token expiration
#         if top_tracks_response.status_code == 401 and 'expired' in top_tracks_response.text:
#             # Token expired, try refreshing it
#             new_access_token = refresh_spotify_token(refresh_token)
#             if not new_access_token:
#                 return JsonResponse({'error': 'Error refreshing Spotify token.'}, status=500)
            
#             # Save the new access token in the session
#             request.session['spotify_access_token'] = new_access_token
#             headers['Authorization'] = f'Bearer {new_access_token}'  # Update the headers with the new access token

#             # Retry the API requests with the new token
#             top_tracks_response = requests.get(top_tracks_url, headers=headers)
#             top_artists_response = requests.get(top_artists_url, headers=headers)

#         if top_tracks_response.status_code != 200:
#             return JsonResponse({'error': 'Error fetching top tracks from Spotify API.'}, status=500)
#         if top_artists_response.status_code != 200:
#             return JsonResponse({'error': 'Error fetching top artists from Spotify API.'}, status=500)

#         # Step 3: Process the data
#         top_tracks_data = top_tracks_response.json()  # Parse the JSON response for top tracks
#         top_artists_data = top_artists_response.json()  # Parse the JSON response for top artists

#         if not top_tracks_data.get('items') or not top_artists_data.get('items'):
#             return JsonResponse({'error': 'No top tracks or artists found.'}, status=404)

#         top_tracks = process_top_tracks(top_tracks_data)
#         top_artists = process_top_artists(top_artists_data)

#         # Collect all the genres
#         top_genres = get_user_top_genres(access_token, 'short_term')

#         # Determine the term (short, medium, or long)
#         term = request.POST.get('term', 'short_term')
#         if term not in ['short_term', 'medium_term', 'long_term']:
#             return JsonResponse({'error': 'Invalid term specified. Must be one of: short_term, medium_term, long_term.'}, status=400)

#         # Save the wrap data to the database
#         try:
#             wrap_name = f"{term.replace('_', ' ').title()} Wrap {UserSpotifyData.objects.filter(user=request.user, term=term).count() + 1}"
#             wrap = UserSpotifyData.objects.create(
#                 user=request.user,
#                 wrap_name=wrap_name,
#                 top_tracks=top_tracks,
#                 top_artists=top_artists,
#                 term=term,
#                 top_genres=top_genres
#             )
#             return JsonResponse({'success': f'{wrap_name} created successfully.'})

#         except Exception as e:
#             return JsonResponse({'error': f'Error saving wrap: {str(e)}'}, status=500)

#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def create_wrapped(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    if request.method == 'POST':
        # Step 1: Fetch Spotify data (replace with actual access token for authenticated user)
        access_token = request.session.get('spotify_access_token')
        refresh_token = request.session.get('spotify_refresh_token')  # Get the refresh token if available
        if not access_token:
            return JsonResponse({'error': 'No Spotify token found for the user. Please authenticate with Spotify.'}, status=401)

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        # Step 2: Determine the term (short_term, medium_term, long_term)
        term = request.POST.get('term')
        if term not in ['short_term', 'medium_term', 'long_term']:
            return JsonResponse({'error': 'Invalid term specified. Must be one of: short_term, medium_term, long_term.'}, status=400)
        
        # Fetch top tracks and top artists based on the selected time frame
        top_tracks_url = f'https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={term}'
        top_artists_url = f'https://api.spotify.com/v1/me/top/artists?limit=10&time_range={term}'

        # Step 3: Try fetching top tracks and top artists
        top_tracks_response = requests.get(top_tracks_url, headers=headers)
        top_artists_response = requests.get(top_artists_url, headers=headers)

        # Check for token expiration
        if top_tracks_response.status_code == 401 and 'expired' in top_tracks_response.text:
            # Token expired, try refreshing it
            new_access_token = refresh_spotify_token(refresh_token)
            if not new_access_token:
                return JsonResponse({'error': 'Error refreshing Spotify token.'}, status=500)
            
            # Save the new access token in the session
            request.session['spotify_access_token'] = new_access_token
            headers['Authorization'] = f'Bearer {new_access_token}'  # Update the headers with the new access token

            # Retry the API requests with the new token
            top_tracks_response = requests.get(top_tracks_url, headers=headers)
            top_artists_response = requests.get(top_artists_url, headers=headers)

        if top_tracks_response.status_code != 200:
            return JsonResponse({'error': 'Error fetching top tracks from Spotify API.'}, status=500)
        if top_artists_response.status_code != 200:
            return JsonResponse({'error': 'Error fetching top artists from Spotify API.'}, status=500)

        # Step 4: Process the data
        top_tracks_data = top_tracks_response.json()  # Parse the JSON response for top tracks
        top_artists_data = top_artists_response.json()  # Parse the JSON response for top artists

        if not top_tracks_data.get('items') or not top_artists_data.get('items'):
            return JsonResponse({'error': 'No top tracks or artists found.'}, status=404)

        top_tracks = process_top_tracks(top_tracks_data)
        top_artists = process_top_artists(top_artists_data)

        # Collect all the genres (pass the term for time-range)
        top_genres = get_user_top_genres(access_token, term)

        # Step 5: Save the wrap data to the database
        try:
            wrap_name = f"{term.replace('_', ' ').title()} Wrap {UserSpotifyData.objects.filter(user=request.user, term=term).count() + 1}"
            wrap = UserSpotifyData.objects.create(
                user=request.user,
                wrap_name=wrap_name,
                top_tracks=top_tracks,
                top_artists=top_artists,
                term=term,
                top_genres=top_genres
            )
            return JsonResponse({'success': f'{wrap_name} created successfully.'})

        except Exception as e:
            return JsonResponse({'error': f'Error saving wrap: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def refresh_spotify_token(refresh_token):
    url = 'https://accounts.spotify.com/api/token'
    
    # Formulate the Authorization header
    auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    base64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {base64_auth}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def process_top_tracks(data):
    return [track['name'] for track in data.get('items', [])]

def process_top_artists(data):
    return [artist['name'] for artist in data.get('items', [])]

def get_user_top_genres(access_token, term):
    url = f'https://api.spotify.com/v1/me/top/artists?limit=50&time_range={term}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    genres = set()
    for artist in response.json()['items']:
        genres.update(artist.get('genres', []))

    # Return only top 5 genres
    return list(genres)[:5]  # Limit to top 5 genres


@login_required
def wrap_detail(request, wrap_id):
    """Display the details of a specific wrap."""
    try:
        wrap = UserSpotifyData.objects.get(id=wrap_id, user=request.user)
    except UserSpotifyData.DoesNotExist:
        messages.error(request, 'Wrap not found or you do not have access to it.')
        return redirect('dashboard')  # Redirect to the dashboard if the wrap doesn't exist or isn't owned by the user

    # Data for the wrap
    top_tracks = wrap.top_tracks
    top_artists = wrap.top_artists
    top_genres = wrap.top_genres
    term = wrap.term  # short_term, medium_term, or long_term

    return render(request, 'spotify_wrapped/wrap_detail.html', {
        'wrap': wrap,
        'top_tracks': top_tracks,
        'top_artists': top_artists,
        'top_genres': top_genres,
        'term': term,
    })
    

def contact_page(request):
    if request.method == "POST":
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        description = request.POST.get('description')


        # You can store this data or process it here
        subject = f"Feedback from {name}"
        message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{description}"
        from_email = 'group36for2340@gmail.com'  # Sender's email
        recipient_list = ['group36for2340@gmail.com']  # Recipient's email (same as sender in this case)


        # Add a success message (optional)
        try:
            # Send the email
            send_mail(subject, message, from_email, recipient_list)
            success_message = "Thank you for your feedback! Your message has been sent to the developers."
        except Exception as e:
            success_message = "There was an error sending your feedback. Please try again later."
            print(f"Email Error: {e}")
            
        return render(request, 'accounts/contact.html', {'success_message': success_message})

    return render(request, 'accounts/contact.html')

