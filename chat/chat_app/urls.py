from django.urls import path
from django.contrib.staticfiles.urls import static
from django.conf import settings

from .views import main_views, auth_views, chat_views


app_name = 'chat_app'

urlpatterns = [
    path('', main_views.MainPageView.as_view(), name='main_page_view'),
    path('profile/<int:pk>/', main_views.UserProfileView.as_view(), name='user_profile_view'),

    # AUTH
    path('sign-up/', auth_views.RegisterView.as_view(), name='register_view'),
    path('login/', auth_views.LoginView.as_view(), name='login_view'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout_view'),

    # CHATS
    path('groups/', chat_views.ListChatsView.as_view(), name='list_group_view'),
    path('groups/create/', chat_views.CreateNewChat.as_view(), name='create_group_view'),
    path('group/<int:pk>/', chat_views.ChatDetail.as_view(), name='group_detail_view'),

    # PERSONAL
    path('personal/<int:pk>/', chat_views.PersonalChatView.as_view(), name='personal_chat_view')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
