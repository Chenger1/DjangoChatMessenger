from django.urls import path

from .views import auth_views


app_name = 'chat_rest'


urlpatterns = [
    path('login/', auth_views.AuthView.as_view(), name='auth_view'),
]
