from django.urls import include, path
from rest_framework.authtoken import views as authtoken_views
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('', include('users.urls')),
    path('', include('recipes.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
] 