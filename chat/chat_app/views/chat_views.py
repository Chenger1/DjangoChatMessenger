from django.views.generic import ListView

from _db.models import Group


class ListGroupView(ListView):
    model = Group
    template_name = 'chats/groups.html'
    context_object_name = 'instances'
