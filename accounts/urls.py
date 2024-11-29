from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete_account/', views.delete_account, name='delete_account'),  # New URL for account deletion
    path('spotify_login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('create-wrapped/', views.create_wrapped, name='create_wrapped'),
]