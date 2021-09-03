from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError

User = get_user_model()


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password',
                                                             'placeholder': 'Your password'}))

    class Meta:
        model = User
        fields = ('username', 'password')


class SignUpForm(UserForm):
    password2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password',
                                                              'placeholder': 'Your password again'}))

    class Meta:
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise ValidationError('Different passwords')
        user.set_password(password)
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password',
                                                             'placeholder': 'Your password'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise ValidationError('There is no such user')
        return username

    def authenticate(self, request):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        user = authenticate(request, username=username, password=password)
        if not user:
            raise ValidationError('Invalid credentials')
        return user
