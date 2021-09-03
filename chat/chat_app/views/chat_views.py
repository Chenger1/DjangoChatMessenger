from django.views.generic import ListView, View
from django.shortcuts import redirect, render

from _db.models import Group
from ..forms import chat
from ..permissions import LoginRequired


class ListGroupView(ListView):
    model = Group
    template_name = 'chats/groups.html'
    context_object_name = 'instances'


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
