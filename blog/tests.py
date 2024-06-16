from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Topic, Entry, Rating, FriendsGroup, FriendCandidates, ServiceContent
from .tools import get_obj_or_create, get_rating, get_topics_data



class BlogTestCase(TestCase):

    TOPIC_1_TEXT = "public topic"
    TOPIC_2_TEXT_1 = ""
    TOPIC_2_TEXT_2 = "lorem ipsum"
    ENTRY_1_TEXT = "Entry from user"
    ENTRY_2_TEXT = ""
    USERNAME_1 = "user"
    USERNAME_2 = "User2"
    TOPIC_1_PERMISSION = Topic.Permissions.FOR_ALL
    RATING_VAL = 5

    def setUp(self):
        self.user = User.objects.create_user(username=self.USERNAME_1, password='pass')
        self.user2 = User.objects.create_user(username=self.USERNAME_2, password='pass')
        self.topic1 = Topic.objects.create(text=self.TOPIC_1_TEXT, user=self.user, permission=self.TOPIC_1_PERMISSION)
        self.topic2 = Topic.objects.create(text=self.TOPIC_2_TEXT_1, user=self.user2, permission=Topic.Permissions.PRIVATE)
        self.entry1 = Entry.objects.create(text=self.ENTRY_1_TEXT, topic=self.topic1, avg_rating=self.RATING_VAL)
        self.entry2 = Entry.objects.create(text=self.ENTRY_2_TEXT, topic=self.topic2)
        Rating.objects.create(publication=self.entry1, user=self.user2, rating=self.RATING_VAL)

    def test_topic(self):
        '''testing topic model'''
        topic1 = Topic.objects.get(user=self.user)
        self.assertEqual(topic1.text, self.TOPIC_1_TEXT)
        self.assertTrue(topic1.permission, self.TOPIC_1_PERMISSION)
        self.assertTrue(topic1.is_valid_topic())
        topic2 = Topic.objects.get(user=self.user2)
        self.assertFalse(topic2.is_valid_topic())
        topic2.text = self.TOPIC_2_TEXT_2
        topic2.save()
        changed_topic = Topic.objects.get(user=self.user2)
        self.assertTrue(changed_topic.is_valid_topic())

    def test_entry(self):
        '''testing entry model'''
        topic = Topic.objects.get(user=self.user)
        entry = Entry.objects.get(topic=topic)
        self.assertEqual(entry.text, self.ENTRY_1_TEXT)
        self.assertEqual(entry.avg_rating, self.RATING_VAL)
        self.assertTrue(entry.is_valid_entry())
        topic2 = Topic.objects.get(user=self.user2)
        entry2 = Entry.objects.get(topic=topic2)
        self.assertFalse(entry2.is_valid_entry())

    def test_rating(self):
        '''Testing permitted assessment'''
        topic = Topic.objects.get(user=self.user)
        own_entry = Entry.objects.get(topic=topic)
        creator_user = own_entry.topic.user
        rating_user = self.user
        if rating_user == creator_user:
            with self.assertRaises(Rating.DoesNotExist):
                Rating.objects.get(publication=own_entry, user=rating_user)
        else:
            Rating.objects.create(publication=own_entry, user=rating_user, rating=5)
            self.assertIsNotNone(Rating.objects.get(publication=own_entry, user=rating_user))

    def test_index(self):
        '''test index page'''
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        pub_topic = Topic.objects.get(user=self.user)
        priv_topic = Topic.objects.get(user=self.user2)
        self.assertTrue(pub_topic in response.context['pub_aside_topics'])
        self.assertFalse(priv_topic in response.context['pub_aside_topics'])

    def test_get_topic_page(self):
        '''test show topic page'''
        pub_topic = Topic.objects.get(user=self.user)
        priv_topic = Topic.objects.get(user=self.user2)
        nocorrect_id = Topic.objects.all().count() + 1
        response_ok = self.client.get(reverse('blog:show_topic', args=[pub_topic.id]))
        response_not_found = self.client.get(reverse('blog:show_topic', args=[nocorrect_id]))
        response_denied = self.client.get(reverse('blog:show_topic', args=[priv_topic.id]))
        self.assertEqual(response_ok.status_code, 200)
        self.assertEqual(response_denied.status_code, 404)
        self.assertEqual(response_not_found.status_code, 404)

    def test_add_friend_without_request(self):
        '''test adding a friend without request (illegal)'''
        self.client.login(username=self.USERNAME_1, password='pass')
        response = self.client.post(reverse('blog:add_friend', args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        friends_group = get_obj_or_create(FriendsGroup, owner=self.user)
        self.assertNotIn(self.user2, friends_group.membership.all())

    def test_add_friend_with_request(self):
        '''test adding a friend with request (legal)'''
        self.client.login(username=self.USERNAME_1, password='pass')
        user2_requests = get_obj_or_create(FriendCandidates, owner=self.user2)
        user2_requests.membership.add(self.user)
        response = self.client.post(reverse('blog:add_friend', args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        friends_group = get_obj_or_create(FriendsGroup, owner=self.user)
        self.assertIn(self.user2, friends_group.membership.all())

    def test_remove_friend(self):
        '''test removing a friend'''
        friends_group = get_obj_or_create(FriendsGroup, owner=self.user)
        friends_group.membership.add(self.user2)
        self.client.login(username=self.USERNAME_1, password='pass')
        response = self.client.post(reverse('blog:remove_friend', args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user2, friends_group.membership.all())

    def test_add_request(self):
        '''test sending a friend request'''
        self.client.login(username=self.USERNAME_1, password='pass')
        response = self.client.post(reverse('blog:add_request', args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        friend_candidates = get_obj_or_create(FriendCandidates, owner=self.user)
        self.assertIn(self.user2, friend_candidates.membership.all())

    def test_remove_request(self):
        '''test removing a friend request'''
        friend_candidates = get_obj_or_create(FriendCandidates, owner=self.user)
        friend_candidates.membership.add(self.user2)
        self.client.login(username=self.USERNAME_1, password='pass')
        response = self.client.post(reverse('blog:remove_request', args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user2, friend_candidates.membership.all())

    def test_social_page(self):
        '''test social page'''
        self.client.login(username=self.USERNAME_1, password='pass')
        response = self.client.get(reverse('blog:social'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('friends', response.context)
        self.assertIn('not_friends', response.context)
        self.assertIn('my_requests', response.context)
        self.assertIn('requests_from_others', response.context)

    def test_welcome_page(self):
        '''test welcome page'''
        response = self.client.get(reverse('blog:welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message_str', response.context)

    def test_about_page(self):
        '''test about page'''
        about_content = ServiceContent.objects.create(name='about', text='About us content')
        response = self.client.get(reverse('blog:about'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('about', response.context)
        self.assertEqual(response.context['about'].text, 'About us content')

