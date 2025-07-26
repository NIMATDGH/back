from rest_framework import generics
from .models import Server
from .serializers import ServerSerializer,UserSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated


class ServerListView(generics.ListAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes=[IsAuthenticated]
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    



