from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Add a view for the root path
    path('set-language/', views.set_language, name='set_language'),
    path('share/', views.share_wrapped, name='share_wrapped'),
]
