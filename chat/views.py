# chat/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Message
from django.urls import reverse_lazy
from .forms import MessageForm
from django.shortcuts import get_object_or_404

class ChatListView(ListView):
    model = Chat
    template_name = 'chat/chat_list.html'

class ChatCreateView(LoginRequiredMixin, CreateView):
    model = Chat
    fields = ['title']
    template_name = 'chat/chat_form.html'
    success_url = reverse_lazy('chat:chat_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class MessageListView(ListView):
    model = Message
    template_name = 'chat/message_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_pk'] = self.kwargs['pk'] 
        return context


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'chat/message_form.html'

    def form_valid(self, form):
        chat = get_object_or_404(Chat, pk=self.kwargs['pk'])
        form.instance.chat = chat
        form.instance.author = self.request.user
        return super().form_valid(form)