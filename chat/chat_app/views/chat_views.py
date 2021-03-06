from django.views.generic import ListView, View
from django.shortcuts import redirect, render
from django.db.models import Q

from _db.models import Group, User, PersonalChat
from ..forms import chat
from ..permissions import LoginRequired


class ListAllChatsView(LoginRequired, ListView):
    template_name = 'chats/groups.html'
    model = Group
    context_object_name = 'instances'


class ListChatsView(LoginRequired, View):
    template_name = 'chats/groups.html'

    def get(self, request):
        groups = Group.objects.filter(Q(owner=request.user) | Q(users=request.user)).distinct()
        personal_chats = PersonalChat.objects.filter(Q(sender=request.user) | Q(receiver=request.user))

        return render(request, self.template_name, context={'instances': groups,
                                                            'chats': personal_chats})


class CreateNewChat(LoginRequired, View):
    def post(self, request):
        form = chat.CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            return redirect('chat_app:group_detail_view', pk=group.pk)
        return redirect('chat_app:list_group_view')


class ChatDetail(LoginRequired, View):
    template_name = 'chats/group.html'

    def get(self, request, pk):
        group = Group.objects.filter(pk=pk).first()
        if not group:
            return redirect('chat_app:main_page_view')
        return render(request, self.template_name, context={'group': group})


class CreatePersonalChatView(LoginRequired, View):
    template_name = 'chats/personal.html'

    def get(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return redirect('chat_app:main_page_view')
        chat_obj = PersonalChat.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).\
            filter(Q(sender=user) | Q(receiver=user)).first()
        if not chat_obj:
            chat_obj = PersonalChat.objects.create(sender=request.user, receiver=user)
        return render(request, self.template_name, context={'user': user,
                                                            'chat': chat_obj})


class PersonalChatView(LoginRequired, View):
    template_name = 'chats/personal.html'

    def get(self, request, pk):
        chat_obj = PersonalChat.objects.filter(pk=pk).first()
        if not chat_obj:
            return redirect('chat_app:main_page_view')
        return render(request, self.template_name, context={'chat': chat_obj})


class LeaveChatGroup(View):
    def get(self, request, pk):
        group = Group.objects.filter(pk=pk).first()
        if group:
            if group.owner != request.user:
                group.users.remove(request.user)
        return redirect('chat_app:main_page_view')
