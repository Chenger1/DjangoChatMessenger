from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from _db.models import User


class AuthView(APIView):
    authentication_classes = []

    def get(self, request, format=None):
        """
        This authentication is only for 'learning' purposes. On the case to understand how to use channels with RestApi
        In production we HAVE to implement or use real auth system
        """
        username = request.query_params.get('username')
        user = User.objects.get(username=username)
        token, _ = Token.objects.get_or_create(user=user)
        content = {
            'user': user.username,
            'token': str(token)
        }
        return Response(content)
