from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Message
from django.urls import reverse_lazy
from .forms import MessageForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ChatListView(ListView):
    model = Chat
    template_name = 'chat/chat_list.html'

@method_decorator(login_required, name='dispatch')
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
        chat = get_object_or_404(Chat, pk=self.kwargs['pk'])
        context['chat'] = chat
        return context

@method_decorator(login_required, name='dispatch')
class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'chat/message_form.html'

    def get_initial(self):
        initial = super().get_initial()
        reply_to_id = self.request.GET.get('reply_to')
        if reply_to_id:
            initial['reply_to'] = get_object_or_404(Message, pk=reply_to_id)
        return initial

    def form_valid(self, form):
        chat = get_object_or_404(Chat, pk=self.kwargs['pk'])
        form.instance.chat = chat
        form.instance.author = self.request.user
        return super().form_valid(form)