from django.urls import path
from .views import ServerListView,UserCreateView

urlpatterns = [
    path('servers/', ServerListView.as_view(), name='server-list'),
    path('users/', UserCreateView.as_view(), name='user-create'),
]