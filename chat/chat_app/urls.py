from django.urls import path
from django.contrib.staticfiles.urls import static
from django.conf import settings

from .views import main_views


app_name = 'chat_app'

urlpatterns = [
    path('', main_views.MainPageView.as_view(), name='main_page_view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
