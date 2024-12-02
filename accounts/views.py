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
from accounts.utils import get_lyric_snippet
import random
import openai
# from transformers import pipeline
# from huggingface_hub import InferenceClient


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


@login_required
def create_wrapped(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    access_token = request.session.get('spotify_access_token')
    refresh_token = request.session.get('spotify_refresh_token')

    if not access_token:
        return JsonResponse({'error': 'No Spotify token found. Please authenticate with Spotify.'}, status=401)

    term = request.POST.get('term')
    valid_terms = ['short_term', 'medium_term', 'long_term']
    if term not in valid_terms:
        return JsonResponse({'error': 'Invalid term specified.'}, status=400)

    headers = {'Authorization': f'Bearer {access_token}'}
    top_tracks_url = f'https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={term}'
    top_artists_url = f'https://api.spotify.com/v1/me/top/artists?limit=10&time_range={term}'

    # Debugging Spotify API request
    print(f"Access Token: {access_token}")
    print(f"Top Tracks URL: {top_tracks_url}")
    print(f"Headers: {headers}")

    # Fetch top tracks and artists
    top_tracks_response = requests.get(top_tracks_url, headers=headers)
    top_artists_response = requests.get(top_artists_url, headers=headers)

    if top_tracks_response.status_code == 401:
        print("Access token expired, attempting refresh.")
        new_access_token = refresh_spotify_token(refresh_token)
        if not new_access_token:
            return JsonResponse({'error': 'Failed to refresh Spotify token.'}, status=500)

        request.session['spotify_access_token'] = new_access_token
        headers['Authorization'] = f'Bearer {new_access_token}'

        # Retry the API requests with the new token
        top_tracks_response = requests.get(top_tracks_url, headers=headers)
        top_artists_response = requests.get(top_artists_url, headers=headers)

    # Handle errors from Spotify API
    if top_tracks_response.status_code != 200:
        print(f"Top Tracks Error: {top_tracks_response.status_code}, {top_tracks_response.text}")
        return JsonResponse({'error': 'Error fetching top tracks from Spotify API.'},
                            status=top_tracks_response.status_code)

    if top_artists_response.status_code != 200:
        print(f"Top Artists Error: {top_artists_response.status_code}, {top_artists_response.text}")
        return JsonResponse({'error': 'Error fetching top artists from Spotify API.'},
                            status=top_artists_response.status_code)

    # Process the data
    top_tracks_data = top_tracks_response.json()
    top_artists_data = top_artists_response.json()

    if not top_tracks_data.get('items') or not top_artists_data.get('items'):
        return JsonResponse({'error': 'No top tracks or artists found.'}, status=404)

    top_tracks = process_top_tracks(top_tracks_data)
    top_artists = process_top_artists(top_artists_data)
    top_genres = process_top_genres(access_token, term)

    # Generate LLM description
    try:
        llm_description = generate_personality_description(top_artists, top_genres, top_tracks)
    except Exception as e:
        print(f"LLM Generation Error: {str(e)}")
        llm_description = "Could not generate description. Error occurred."

    # Save the wrap
    try:
        wrap_name = f"{term.replace('_', ' ').title()} Wrap {UserSpotifyData.objects.filter(user=request.user, term=term).count() + 1}"
        wrap = UserSpotifyData.objects.create(
            user=request.user,
            wrap_name=wrap_name,
            top_tracks=top_tracks_data,
            top_artists=top_artists_data,
            term=term,
            top_genres=top_genres,
            llm_description=llm_description,
        )
        return JsonResponse({'success': f'{wrap_name} created successfully.'})
    except Exception as e:
        print(f"Database Save Error: {str(e)}")
        return JsonResponse({'error': 'Error saving wrap data.'}, status=500)


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

def process_top_genres(access_token, term):
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


@never_cache
@login_required(login_url='login')
def wrap_detail(request, wrap_id):
    try:
        # Fetch wrap data for the given wrap_id
        wrap = UserSpotifyData.objects.get(user=request.user, id=wrap_id)
        top_tracks = wrap.top_tracks

        # Ensure we have the correct access_token for the logged-in user
        access_token = request.session.get('spotify_access_token')

        if not access_token:
            return redirect('spotify_login')

        # Get user top artists and genres
        top_artists = wrap.top_artists
        top_genres = wrap.top_genres
        llm_description = wrap.llm_description
        # print(f"LLM Description: {llm_description}")
        term = wrap.term

        # Format the top tracks
        formatted_tracks = []
        for track in top_tracks.get('items', [])[:5]:
            track_name = track['name']
            artists = ', '.join(artist['name'] for artist in track['artists'])
            formatted_tracks.append({'track_name': track_name, 'artists': artists})

        # Initialize context with Wrapped data
        context = {
            'wrap_name': wrap.wrap_name,
            'top_tracks': formatted_tracks,
            'top_artists': top_artists.get('items', []),
            'top_genres': top_genres,
            'term': term,
            'llm_description': llm_description,
        }

        # Initialize 'scores' and 'correct_songs' in session if not already set
        if 'scores' not in request.session:
            request.session['scores'] = {}
        if 'correct_songs' not in request.session:
            request.session['correct_songs'] = {}

        # Convert wrap_id to string because session keys must be strings
        wrap_id_str = str(wrap_id)

        # Initialize score and correct_song for this wrap if not present
        if wrap_id_str not in request.session['scores']:
            request.session['scores'][wrap_id_str] = 0

        if request.method == 'POST':
            if 'timeout' in request.POST:
                # User ran out of time
                correct_song = request.session['correct_songs'].get(wrap_id_str, '')
                context['game_result'] = f"Time's up! The correct answer was {correct_song}."
                request.session['scores'][wrap_id_str] -= 5  # Deduct points for timeout
            else:
                # Handle the user's guess
                user_guess = request.POST.get('guess')
                correct_song = request.session['correct_songs'].get(wrap_id_str, '').lower()

                if user_guess.lower() == correct_song.lower():
                    context['game_result'] = 'Correct! 🎉'
                    request.session['scores'][wrap_id_str] += 10  # Add 10 points
                else:
                    context['game_result'] = f'Wrong! The correct answer was {correct_song}.'
                    request.session['scores'][wrap_id_str] -= 5  # Deduct 5 points

            # Generate a new song for the next game
            selected_track = random.choice(top_tracks.get('items', []))
            song_name = selected_track['name']
            artist_name = selected_track['artists'][0]['name']
            snippet = get_lyric_snippet(song_name, artist_name)

            # Handle case when no lyrics are found
            if snippet is None:
                snippet = "Sorry, no lyrics available for this song."

            # Store the correct song name in the session for this wrap
            request.session['correct_songs'][wrap_id_str] = song_name

            # Add lyrics game data to context
            context.update({
                'snippet': snippet,
                'artist_name': artist_name,
            })

        else:
            # Reset the result on a new question
            context['game_result'] = None
            selected_track = random.choice(top_tracks.get('items', []))
            song_name = selected_track['name']
            artist_name = selected_track['artists'][0]['name']
            snippet = get_lyric_snippet(song_name, artist_name)

            # Handle case when no lyrics are found
            if snippet is None:
                snippet = "Sorry, no lyrics available for this song."

            # Store the correct song name in the session for this wrap
            request.session['correct_songs'][wrap_id_str] = song_name

            # Add lyrics game data to context
            context.update({
                'snippet': snippet,
                'artist_name': artist_name,
            })

        # Include the score for this wrap in the context
        context['score'] = request.session['scores'][wrap_id_str]

        # Mark the session as modified to ensure it gets saved
        request.session.modified = True

        return render(request, 'spotify_wrapped/wrap_detail.html', context)

    except UserSpotifyData.DoesNotExist:
        messages.error(request, 'Wrap not found or you do not have access to it.')
        return redirect('dashboard')  # Redirect to the dashboard if the wrap doesn't exist or isn't owned by the user

    # # Data for the wrap
    # top_tracks = wrap.top_tracks
    # top_artists = wrap.top_artists
    # top_genres = wrap.top_genres
    # term = wrap.term  # short_term, medium_term, or long_term
    # llm_description = wrap.llm_description

    # return render(request, 'spotify_wrapped/wrap_detail.html', {
    #     'wrap': wrap,
    #     'top_tracks': top_tracks,
    #     'top_artists': top_artists,
    #     'top_genres': top_genres,
    #     'term': term,
    #     'llm_description': llm_description,
    # })
    

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


# def generate_llm_description(artists, genres, tracks):
#     """
#     Generate a description using a Hugging Face text-generation model.
#     :param artists: List of top artists.
#     :param genres: List of top genres.
#     :param tracks: List of top tracks.
#     :return: Generated description as a string.
#     """
#     # Load the text generation pipeline
#     generator = pipeline("text-generation", model="gpt2")  # You can replace "gpt2" with a better model if needed.

#     # Create the prompt for the model
#     prompt = (
#         f"Describe a person who listens to artists like {', '.join(artists[:3])}, "
#         f"enjoys genres like {', '.join(genres[:3])}, and listens to tracks such as "
#         f"{', '.join([track['name'] for track in tracks[:3]])}."
#     )

#     # Generate the description
#     response = generator(prompt, max_length=100, num_return_sequences=1)

#     # Return the generated text
#     return response[0]['generated_text']

# def generate_llm_description(artists, genres, tracks):
#     try:
#         # Initialize the Hugging Face Inference API
#         client = InferenceClient(model="bigscience/bloomz-1b7", token=settings.LLM_API_KEY)

#         # Construct the input prompt
#         # prompt = (
#         #     f"Describe a person who listens to artists like {', '.join(artists[:3])}, "
#         #     f"enjoys genres like {', '.join(genres[:3])}, and listens to tracks such as "
#         #     f"{', '.join([track['name'] for track in tracks[:3]])}."
#         # )
#         prompt = (
#             "You are a music analyst. Describe the personality of a person who enjoys the following music:\n"
#             "Top tracks: Love Story, Blank Space, Shake It Off.\n"
#             "Top artists: Taylor Swift, Ed Sheeran, Dua Lipa.\n"
#             "Top genres: Pop, Acoustic, Indie.\n"
#             "Provide insights about their likely personality, hobbies, and lifestyle."
#         )

#         response = client.text_generation(prompt, max_new_tokens=50)
#         print("Raw response:", response)  # Print the raw response
#         print("Response type:", type(response))  # Check the type of the response

#         # Ensure the response is a string or extract the text
#         if isinstance(response, str):
#             return response
#         elif isinstance(response, dict):
#             return response.get("generated_text", "Could not extract text from response.")
#         else:
#             return "Unexpected response format."
#     except Exception as e:
#         print(f"Error with Hugging Face Inference API: {e}")
#         return "Could not generate description. Error occurred."


def generate_personality_description(artists, genres, tracks):
    try:
        # Set up the OpenAI API key
        openai.api_key = settings.LLM_API_KEY
        print("artits", artists[:3])
        print("Genres:", genres[:3])
        print("Tracks:", tracks[:3])
        # Construct the input prompt
        prompt = (
            f"Imagine a person who listens to artists like {', '.join(artists[:3])}, "
            f"enjoys genres such as {', '.join(genres[:3])}, and their favorite tracks are "
            f"{', '.join(tracks[:3])}.\n"
            "Describe their personality, hobbies, and interests in detail. Respond in second person and do not say the artist, genre, and tracks in your description. Focus more on adjectives and less preferences. Answer consiely in ONLY 2-3 sentences and do not cut off in the middle."
        )
        # prompt = (
        #     "You are a music analyst. Describe the personality of a person who enjoys the following music:\n"
        #     "Top tracks: Love Story, Blank Space, Shake It Off.\n"
        #     "Top artists: Taylor Swift, Ed Sheeran, Dua Lipa.\n"
        #     "Top genres: Pop, Acoustic, Indie.\n"
        #     "Provide insights about their likely personality, hobbies, and lifestyle."
        # )

        # Send the prompt to OpenAI API

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" for better results if available
            messages=[
                {"role": "system", "content": "You are a helpful assistant and music analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        #print("raw_response", response['choices'][0]['message']['content'].strip(), type(response))
        # Extract the generated text
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "Error occurred while generating description."