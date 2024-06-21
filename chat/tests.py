from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Chat, Message


class ChatTests(TestCase):

    DEFAULT_PWD = '12345'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password=cls.DEFAULT_PWD)
        cls.other_user = User.objects.create_user(username='otheruser', password=cls.DEFAULT_PWD)
        cls.chat = Chat.objects.create(title='Test Chat')
        cls.message = Message.objects.create(chat=cls.chat, author=cls.user, content='Test Message')

    def test_chat_list_view(self):
        response = self.client.get(reverse('chat:chat_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Chat')
        self.assertTemplateUsed(response, 'chat/chat_list.html')

    def test_chat_create_view(self):
        self.client.login(username='testuser', password=self.DEFAULT_PWD)
        response = self.client.post(reverse('chat:chat_create'), {'title': 'New Chat'})
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(Chat.objects.count(), 2)
        self.assertEqual(Chat.objects.last().title, 'New Chat')

    def test_chat_create_view_without_login(self):
        response = self.client.post(reverse('chat:chat_create'), {'title': 'New Chat'})
        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertEqual(response.url, '/users/login/?next=/chat/create/')
        self.assertEqual(Chat.objects.count(), 1)  # No new chat created

    def test_message_list_view(self):
        response = self.client.get(reverse('chat:message_list', kwargs={'pk': self.chat.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Message')
        self.assertTemplateUsed(response, 'chat/message_list.html')

    def test_message_create_view(self):
        self.client.login(username='testuser', password=self.DEFAULT_PWD)
        response = self.client.post(reverse('chat:message_create', kwargs={'pk': self.chat.pk}), {'content': 'New Message'})
        self.assertEqual(response.status_code, 302)  # Redirects after success
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(Message.objects.last().content, 'New Message')

    def test_message_create_view_without_login(self):
        response = self.client.post(reverse('chat:message_create', kwargs={'pk': self.chat.pk}), {'content': 'New Message'})
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(response.url, f'/users/login/?next=/chat/{self.chat.pk}/messages/create/')
        self.assertEqual(Message.objects.count(), 1)





def test_message_create_with_invalid_reply(self):
    self.client.login(username='testuser', password=self.DEFAULT_PWD)
    response = self.client.post(reverse('chat:message_create', kwargs={'pk': self.chat.pk}), {'content': ''})
    self.assertEqual(response.status_code, 200)

    form = response.context['form']
    self.assertTrue(form.errors)  # Перевіряємо наявність помилок у формі
    self.assertEqual(form.errors['content'], ['This field is required.'])  # Перевіряємо конкретну помилку
    self.assertEqual(Message.objects.count(), 1)  # Переконуємося, що повідомлення не створилося




    def test_reply_message_display(self):
        reply_message = Message.objects.create(chat=self.chat, author=self.other_user, content='Reply Message', reply_to=self.message)
        response = self.client.get(reverse('chat:message_list', kwargs={'pk': self.chat.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reply Message')
        self.assertContains(response, 'Test Message')
        self.assertTemplateUsed(response, 'chat/message_list.html')

def test_message_create_with_reply(self):
    self.client.login(username='testuser', password=self.DEFAULT_PWD)
    response = self.client.post(reverse('chat:message_create', kwargs={'pk': self.chat.pk}) + f'?reply_to={self.message.pk}', {'content': 'Reply Message'})
    self.assertEqual(response.status_code, 302)  # Redirects after success
    self.assertEqual(Message.objects.count(), 2)
    self.assertEqual(Message.objects.last().content, 'Reply Message')
    self.assertEqual(Message.objects.last().reply_to, self.message)
