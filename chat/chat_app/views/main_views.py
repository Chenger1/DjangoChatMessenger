from django.views.generic import TemplateView, DetailView

from ..permissions import LoginRequired

from _db.models import User


class MainPageView(TemplateView):
    template_name = 'index.html'


class UserProfileView(LoginRequired, DetailView):
    template_name = 'profile.html'
    model = User
    context_object_name = 'instance'
