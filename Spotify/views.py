from django.utils.translation import activate
from django.shortcuts import redirect
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse


def set_language(request):
    """
    Handles the language toggle functionality.
    """
    if request.method == "POST":
        language = request.POST.get("language", "en")  # Default to English
        activate(language)
        # Redirect back to the previous page or to the home page
        return redirect(request.META.get("HTTP_REFERER", "/"))
    else:
        # Handle GET requests
        return HttpResponse(
            "This endpoint is for POST requests only to set the language.",
            status=405,
        )


def generate_wrapped_image(data):
    image = Image.new("RGB", (800, 600), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(f"{settings.BASE_DIR}/static/fonts/arial.ttf", 40)
    draw.text(
        (50, 50),
        f"Your Spotify Wrapped\nTop Artist: {data['artist']}",
        fill="black",
        font=font,
    )
    image_path = f"media/wrapped/{data['user_id']}_wrapped.png"
    image.save(image_path)
    return image_path


def share_wrapped(request):
    if request.method == "POST":
        data = {"user_id": request.user.id, "artist": "Taylor Swift"}
        image_path = generate_wrapped_image(data)
        shareable_url = f"{request.build_absolute_uri('/')}{image_path}"
        return JsonResponse({"shareable_url": shareable_url})
