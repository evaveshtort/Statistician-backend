from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .models import CustomUser
import redis

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

class SessionIDAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            session_id = request.COOKIES["session_id"]
        except:
            return None
        
        try:
            email = session_storage.get(session_id)
        except:
            return None
        try:
            user = CustomUser.objects.get(email=email)
        except:
            raise AuthenticationFailed("Пользователь не найден")

        return (user, None)
