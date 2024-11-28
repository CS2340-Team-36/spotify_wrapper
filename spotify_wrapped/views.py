from django.utils.translation import activate
from django.shortcuts import redirect
from django.http import JsonResponse
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings


def set_language(request):
    """
    Handles the language toggle functionality.
    """
    if request.method == "POST":
        language = request.POST.get("language", "en")  # Default to English
        activate(language)
        # Redirect back to the previous page or to the home page
        return redirect(request.META.get("HTTP_REFERER", "/"))


def generate_wrapped_image(data):
    """
    Generates a Spotify Wrapped image with user data.
    """
    # Create a blank image
    image = Image.new("RGB", (800, 600), (255, 255, 255))  # White background
    draw = ImageDraw.Draw(image)

    # Define the font and text to be drawn
    font_path = f"{settings.BASE_DIR}/static/fonts/arial.ttf"  # Update path if necessary
    try:
        font = ImageFont.truetype(font_path, 40)
    except OSError:
        raise Exception(f"Font file not found at {font_path}. Please ensure it exists.")

    # Draw user data onto the image
    text = f"Your Spotify Wrapped\nTop Artist: {data['artist']}"
    draw.text((50, 50), text, fill="black", font=font)

    # Save the image to the media folder
    image_path = f"media/wrapped/{data['user_id']}_wrapped.png"
    full_path = f"{settings.BASE_DIR}/{image_path}"
    image.save(full_path)

    return image_path


def share_wrapped(request):
    """
    Handles the generation of a shareable Spotify Wrapped image.
    """
    if request.method == "POST":
        # Dummy data for user; replace with actual Spotify data integration
        data = {
            "user_id": request.user.id if request.user.is_authenticated else "guest",
            "artist": "Taylor Swift",
        }

        # Generate the Wrapped image
        try:
            image_path = generate_wrapped_image(data)
            shareable_url = f"{request.build_absolute_uri('/')}{image_path}"
            return JsonResponse({"shareable_url": shareable_url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # If the request is not POST, return an error
    return JsonResponse({"error": "Invalid request method"}, status=400)

from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to Spotify Wrapped!</h1>")