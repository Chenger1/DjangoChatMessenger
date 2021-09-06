from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response


class AuthView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        content = {
            'user': request.user.username,
            'auth': str(request.auth)
        }
        return Response(content)
