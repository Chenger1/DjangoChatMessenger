from django.test import TestCase

from _db.models import User

class TestDB(TestCase):
    def test_create_user(self):
        User.objects.create(username='test', password='123')
        user = User.objects.first()
        self.assertEqual(user.username, 'test')
