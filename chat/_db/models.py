from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser

from .manager import UserManager


class User(AbstractBaseUser):
    username = models.CharField(max_length=70, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()


class Message(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User, related_name='groups', on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='groups_in')

    @property
    def owner_username(self):
        return self.owner.username
