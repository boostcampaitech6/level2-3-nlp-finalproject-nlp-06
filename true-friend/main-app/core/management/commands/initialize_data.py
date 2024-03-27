from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile, BotConfiguration
import os

# https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/
class Command(BaseCommand):
    help = 'Initializes data in the database'

    def handle(self, *args, **kwargs):
        # Get the environment variables
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        bot_name = os.environ.get('BOT_NAME')

        # Create a superuser
        User = get_user_model()
        if not User.objects.filter(username='admin').exists(): 
            User.objects.create_superuser(admin_username, f"{admin_username}@email.com", admin_password)

        # Create a profile for the superuser
        if not Profile.objects.filter(user__username=admin_username).exists():
            user = User.objects.get(username=admin_username)
            Profile.objects.create(user=user, name=admin_username.title())

        # Create a profile for the bot
        if not Profile.objects.filter(name=bot_name).exists():
            Profile.objects.create(name=bot_name, profile_image="profiles/jiu.png")
        
        # Select the bot profile as configuration
        if not BotConfiguration.objects.exists():
            bot_profile = Profile.objects.get(name=bot_name)
            BotConfiguration.objects.create(bot_profile=bot_profile)