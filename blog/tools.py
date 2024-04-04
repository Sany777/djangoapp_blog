from django.contrib.auth.models import User

from .models import *
from .forms import *



def get_obj_or_none(modelClass, **kwargs):

    try:
        return modelClass.objects.get(**kwargs)
    except modelClass.DoesNotExist:
        return modelClass.objects.create(**kwargs)
    except:
        pass
    return None



def get_related_users(userModel, user):
    
    users = []
    
    if user.is_authenticated:    

        try:
            users = userModel.objects.get(owner=user).membership.all()
        except userModel.DoesNotExist:
            userModel.objects.create(owner=user)
        except:
            pass
            
    return users


def add_user_to_group(userModel, user_to_add, user, add_user=True):
    
    user_group = None
    if user.is_authenticated:
        try:
            user_group = userModel.objects.get(owner=user)
            if add_user:
                user_group.membership.add(user_to_add)
                user_group.save()
            else:
                user_group.membership.remove(user_to_add)
        except userModel.model.DoesNotExist:
            if add_user:
                user_group = userModel.objects.create(owner=user)
                user_group.save()
                user_group.membership.add(user_to_add)


   
    
def get_topics_data(user, friends_list=None):
    
    user_topics = []
    friends_topics = []
    
    pub_topics = Topic.objects.filter(permision=Topic.Permissions.FOR_ALL)
            
    if user.is_authenticated:
        pub_topics = [topic for topic in pub_topics if topic.user != user]
        user_topics = user.topics.order_by('-pk')
        if friends_list == None:
            friends_list = get_related_users(FriendsGroup, user)
        if friends_list:
            friends_topics = [topic for friend in friends_list for topic in friend.topics.order_by('-pk') if topic.permision != Topic.Permissions.PRIVATE]
            pub_topics = [topic for topic in pub_topics if topic not in friends_topics]

    return (pub_topics, user_topics, friends_topics)


def get_entry_from_topics(topics):
    return [entry for topic in topics for entry in topic.entries.order_by('-pk')]

