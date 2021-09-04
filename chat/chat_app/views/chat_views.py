from django.views.generic import ListView, View
from django.shortcuts import redirect, render
from django.db.models import Q

from _db.models import Group, User, PersonalChat
from ..forms import chat
from ..permissions import LoginRequired


class ListAllChatsView(ListView):
    template_name = 'chats/groups.html'
    model = Group
    context_object_name = 'instances'


class ListChatsView(View):
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
        group = Group.objects.get(pk=pk)
        return render(request, self.template_name, context={'group': group})


class PersonalChatView(LoginRequired, View):
    template_name = 'chats/personal.html'

    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        chat_obj = PersonalChat.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).\
            filter(Q(sender=user) | Q(receiver=user)).first()
        return render(request, self.template_name, context={'user': user,
                                                            'chat': chat_obj})
