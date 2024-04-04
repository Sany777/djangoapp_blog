from django.urls import path
from . import views

app_name = "blog"




urlpatterns = [
    path('about/', views.about, name='about'),
    path('topics/<int:topic_id>/remove', views.remove_topic, name='remove_topic'),
    path('entry/<int:entry_id>/remove', views.remove_entry, name='remove_entry'),
    path('topics/<int:topic_id>/', views.show_topic, name='show_topic'),
    path('topics/<int:topic_id>/<int:topic_start>', views.show_topic, name='show_topic_num'),
    path('topics/new', views.edit_topic, name='new_topic'),
    path('topics/<int:topic_id>/edit', views.edit_topic, name='edit_topic'),
    path('topics/', views.show_topic_list, name='show_topic_list'),
    path('entry/<int:entry_id>/edit', views.edit_entry, name='edit_entry'),
    path('entry/<int:topic_id>/new', views.new_entry, name='new_entry'),
    path('index/', views.index, name='index'),
    path('set_rate/<int:publication_id>', views.set_rate, name='set_rate'),
    path('social/<int:user_id>/remove_request', views.remove_request, name='remove_request'),
    path('social/<int:user_id>/add_friend', views.add_friend, name='add_friend'),
    path('social/<int:user_id>/add_request', views.add_request, name='add_request'),
    path('social/<int:user_id>/remove_friend', views.remove_friend, name='remove_friend'),
    path('social', views.social, name='social'),
    
    path('', views.index, name='index'),

]