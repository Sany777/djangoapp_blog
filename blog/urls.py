from django.urls import path
from . import views

app_name = "blog"




urlpatterns = [
    path('', views.index, name='index'),
    path('topics/<int:topic_id>/', views.show_topic, name='topic'),
    path('topics/', views.topic, name='topics'),
    path('new_topic/', views.new_topic, name='new_topic'),
    path('newentry/<int:topic_id>', views.new_entry, name='new_entry'),
    path('editentry/<int:entry_id>', views.edit_entry, name='edit_entry'),
]