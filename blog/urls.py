from django.urls import path
from . import views

app_name = "blog"


urlpatterns = [
    path('about/', views.about, name='about'),
    path('topics/remove/<int:topic_id>', views.remove_topic, name='remove_topic'),
    path('entry/remove/<int:entry_id>', views.remove_entry, name='remove_entry'),
    path('topics/<int:topic_id>/', views.show_topic, name='show_topic'),
    path('topics/<int:topic_id>/<int:topic_start>', views.show_topic, name='show_topic_num'),
    path('topics/new', views.edit_topic, name='new_topic'),
    path('topics/<int:topic_id>/edit', views.edit_topic, name='edit_topic'),
    path('topics/', views.show_topic_list, name='show_topic_list'),
    path('entry/edit/<int:entry_id>', views.edit_entry, name='edit_entry'),
    path('entry/new/<int:topic_id>', views.new_entry, name='new_entry'),
    path('index/', views.index, name='index'),
    path('set/rate/<int:publication_id>', views.set_rate, name='set_rate'),
    path('social/remove/request/<int:user_id>', views.remove_request, name='remove_request'),
    path('social/add/friend/<int:user_id>', views.add_friend, name='add_friend'),
    path('social/add/request/<int:user_id>', views.add_request, name='add_request'),
    path('social/remove/friend/<int:user_id>', views.remove_friend, name='remove_friend'),
    path('social', views.social, name='social'),
    path('', views.index, name='index'),
]