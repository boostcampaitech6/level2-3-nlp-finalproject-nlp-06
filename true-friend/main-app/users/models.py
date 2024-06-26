from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid
from .choices import GENDER_CHOICES, AGE_CHOICES

# Create your models here.

name_validator = RegexValidator(r'^[ㄱ-ㅎ가-힣][ㄱ-ㅎ가-힣]*[ㄱ-ㅎ가-힣]$', '한글만 입력가능합니다.')

class Profile(models.Model):
    # remove username and email from here (use User model instead)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True, validators=[name_validator]) 
    profile_image = models.ImageField(null=True, blank=True, upload_to="profiles/", default="profiles/user-default.png")
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, blank=True, null=True, default="남성") # 남성 (2 characters)
    age = models.CharField(max_length=3, choices=AGE_CHOICES, blank=True, null=True, default="20대") # 10대 (3 characters)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False) # Primary key, not editable
    created = models.DateTimeField(auto_now_add=True) # Automatically add date and time

    def __str__(self):
        return str(self.name) # Return username as string
    
    class Meta:
        ordering = ["created"] # Created date ascending order 
    
    @property
    def image_url(self):
        try:
            url = self.profile_image.url
        except:
            self.profile_image = "profiles/user-default.png"
            self.save()
            url = self.profile_image.url
        return url



class BotConfiguration(models.Model):
    bot_profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.bot_profile.name} - Bot Configuration'
    


class BotProfile(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True, validators=[name_validator])
    profile_image = models.ImageField(null=True, blank=True, upload_to="profiles/", default="profiles/user-default.png")

    def save(self, *args, **kwargs):
        if BotProfile.objects.exists() and not self.pk:
            raise ValidationError('There can only be one BotProfile instance.')
        return super(BotProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"Singleton BotProfile Instance - {self.name}"
    


class Notice(models.Model):
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name="notices")
    title = models.CharField(max_length=200)
    text = models.TextField()
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    retrospective_id = models.UUIDField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f"{self.title} - {self.receiver.name}"

    class Meta:
        ordering = ["-created"] # Created date descending order