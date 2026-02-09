from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
]