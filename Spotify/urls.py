"""
URL configuration for Spotify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.views.i18n import set_language
from django.shortcuts import redirect


def default_redirect(request):
    # Redirect to the default language (e.g., English)
    return redirect("/en/")


urlpatterns = [
    path("", default_redirect, name="default_redirect"),  # Redirect root URL
    path(
        "set-language/", set_language, name="set_language"
    ),  # Optional: for language switching
]

urlpatterns += i18n_patterns(
    path("", include("spotify_wrapped.urls")),  # Include all app-level URLs here
    path("admin/", admin.site.urls),
)
