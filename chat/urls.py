# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatListView.as_view(), name='chat_list'),
    path('create/', views.ChatCreateView.as_view(), name='chat_create'),
    path('<int:pk>/messages/', views.MessageListView.as_view(), name='message_list'),
    path('<int:pk>/messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    
]
