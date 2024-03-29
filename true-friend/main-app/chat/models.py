from django.db import models
from django.contrib.auth.models import User
from users.models import Profile, BotConfiguration
import uuid

# Create your models here.

class UserMessage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.owner.name} - {self.session.id}'
    
    class Meta:
        ordering = ['created_at']


class BotResponse(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user_message = models.OneToOneField(UserMessage, on_delete=models.CASCADE, related_name='bot_response')
    bot_configuration = models.ForeignKey(BotConfiguration, on_delete=models.CASCADE, default=1)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.session.title}'
    
    class Meta:
        ordering = ['created_at']
    

