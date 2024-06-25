from django.contrib.auth.models import User

from .models import *
from .forms import *


def get_rating(entry: Entry) -> float:
    rating_value = Entry.DEFAULT_RATING
    publication_ratings = Rating.objects.filter(publication=entry)
    total_ratings = publication_ratings.count()
    
    if total_ratings != 0:
        total_score = publication_ratings.aggregate(models.Sum('rating'))['rating__sum']
        rating_value = total_score / total_ratings
    
    return rating_value

def get_obj_or_create(modelClass, user_to_add: User = None, create: bool = True, **kwargs):
    try:
        return modelClass.objects.get(**kwargs)
    except modelClass.DoesNotExist:
        if create:
            model = modelClass.objects.create(**kwargs)
            if user_to_add:
                model.membership.add(user_to_add)
                model.save()
            return model
    except modelClass.MultipleObjectsReturned:
        pass
    
    return None
   
    
def get_topics_data(user: User, friends_list: list[User] = None):
    user_topics = []
    friends_topics = []
    
    pub_topics = Topic.objects.filter(permission=Topic.Permissions.FOR_ALL)
    
    if user.is_authenticated:
        pub_topics = pub_topics.exclude(user=user)
        user_topics = user.topics.order_by('-pk')
        
        if friends_list is None:
            friends_group = get_obj_or_create(FriendsGroup, owner=user)
            if friends_group:
                friends_list = friends_group.membership.all()
        
        if friends_list:
            friends_topics = Topic.objects.filter(user__in=friends_list).exclude(permission=Topic.Permissions.PRIVATE).order_by('-pk')
            pub_topics = pub_topics.exclude(id__in=[topic.id for topic in friends_topics])

    return pub_topics, user_topics, friends_topics


def get_entry_from_topics(topics: list[Topic]):
    return [entry for topic in topics for entry in topic.entries.order_by('-pk')]


def get_requests(user, friends, all_user):
    return [candidate for candidate in all_user if candidate not in friends for u in get_obj_or_create(FriendCandidates, owner=candidate).membership.all() if u == user]
        