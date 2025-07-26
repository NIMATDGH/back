
from django.db import models
from django.contrib.auth.models import User

class Server(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_servers')
    members = models.ManyToManyField(User, related_name='servers')

    def __str__(self):
        return self.name

class Channel(models.Model):
    name = models.CharField(max_length=100)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='channels')

    def __str__(self):
        return f'{self.name} ({self.server.name})'

class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message by {self.author.username} in {self.channel.name}'
# Create your models here.
