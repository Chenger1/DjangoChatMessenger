from django.views.generic import View
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import render, redirect

from ..forms.auth import SignUpForm, LoginForm

User = get_user_model()


class RegisterView(View):
    template_name = 'auth/sign_up.html'
    model = User

    def get(self, request):
        form = SignUpForm()
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user:
                login(request, user)
                return redirect('chat_app:main_page_view')


class LoginView(View):
    template_name = 'auth/login.html'
    model = User

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.authenticate(request)
            if user:
                login(request, user)
                return redirect('chat_app:main_page_view')
        return render(request, self.template_name, context={'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('chat_app:main_page_view')
