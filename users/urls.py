from django.urls import path, include

from . import views

app_name = "users"

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', include('django.contrib.auth.urls')),
]