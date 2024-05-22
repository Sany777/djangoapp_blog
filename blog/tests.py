from django.test import TestCase
from .models import *



class BlogTestCase(TestCase):

    TOPIC_1_TEXT = "public topic"
    TOPIC_2_TEXT_1 = ""
    TOPIC_2_TEXT_2 = "lorem ipsum"
    ENTRY_1_TEXT = "Entry from User1"
    ENTRY_2_TEXT = ""
    USERNAME_1 = "User1"
    USERNAME_2 = "User2"
    TOPIC_1_PERMISSION = Topic.Permissions.FOR_ALL
    RATING_VAL = 5

    def setUp(self):
        user1 = User.objects.create(username=self.USERNAME_1)
        user2 = User.objects.create(username=self.USERNAME_2)
        topic1 = Topic.objects.create(text=self.TOPIC_1_TEXT, user=user1, permission=self.TOPIC_1_PERMISSION)
        topic2 = Topic.objects.create(text=self.TOPIC_2_TEXT_1, user=user2, permission=Topic.Permissions.PRIVATE)
        entry1 = Entry.objects.create(text=self.ENTRY_1_TEXT, topic=topic1, avg_rating=self.RATING_VAL)
        Entry.objects.create(text=self.ENTRY_2_TEXT, topic=topic2)
        Rating.objects.create(publication=entry1, user=user2, rating=self.RATING_VAL)

    def test_topic(self):
        '''testing topic model'''
        user1 = User.objects.get(username=self.USERNAME_1)
        topic1 = Topic.objects.get(user=user1)
        self.assertEqual(topic1.text, self.TOPIC_1_TEXT)
        self.assertTrue(topic1.permission, self.TOPIC_1_PERMISSION)
        self.assertTrue(topic1.is_valid_topic())
        user2 = User.objects.get(username=self.USERNAME_2)
        topic2 = Topic.objects.get(user=user2)
        self.assertFalse(topic2.is_valid_topic())
        topic2.text = self.TOPIC_2_TEXT_2
        topic2.save()
        changed_topic = Topic.objects.get(user=user2)
        self.assertTrue(changed_topic.is_valid_topic())

    def test_entry(self):
        '''testing entry model'''
        user = User.objects.get(username=self.USERNAME_1)
        topic = Topic.objects.get(user=user)
        entry = Entry.objects.get(topic=topic)
        self.assertEqual(entry.text, self.ENTRY_1_TEXT)
        self.assertEqual(entry.avg_rating, self.RATING_VAL)
        self.assertTrue(entry.is_valid_entry())
        user2 = User.objects.get(username=self.USERNAME_2)
        topic2 = Topic.objects.get(user=user2)
        entry2 = Entry.objects.get(topic=topic2)
        self.assertFalse(entry2.is_valid_entry())

    def test_rating(self):
        '''testing permitted assessment'''
        owner = User.objects.get(username=self.USERNAME_1)
        topic = Topic.objects.get(user=owner)
        own_entry = Entry.objects.get(topic=topic)
        self.assertFalse(is_allowed_assessment(owner, own_entry))

    def test_index(self):
        '''test index page'''
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username=self.USERNAME_1)
        user2 = User.objects.get(username=self.USERNAME_2)
        pub_topic = Topic.objects.get(user=user)
        priv_topic = Topic.objects.get(user=user2)
        self.assertTrue(pub_topic in response.context['pub_aside_topics'])
        self.assertFalse(priv_topic in response.context['pub_aside_topics'])

    def test_get_topic_page(self):
        '''test show topic page'''
        user = User.objects.get(username=self.USERNAME_1)
        user2 = User.objects.get(username=self.USERNAME_2)
        nocorect_id = Topic.objects.all().count() + 1
        pub_topic = Topic.objects.get(user=user)
        priv_topic = Topic.objects.get(user=user2)
        response_ok = self.client.get(f'/blog/topics/{pub_topic.id}/')
        response_nofinded = self.client.get(f'/blog/topics/{nocorect_id}/')
        response_denied = self.client.get(f'/blog/topics/{priv_topic.id}/')
        self.assertEqual(response_ok.status_code, 200)
        self.assertEqual(response_denied.status_code, 404)
        self.assertEqual(response_nofinded.status_code, 404)

        

