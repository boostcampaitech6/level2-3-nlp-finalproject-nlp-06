from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(BotConfiguration)

@admin.register(BotProfile)
class SingletonModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # If an instance exists, do not allow adding new ones
        if BotProfile.objects.exists():
            return False
        return super().has_add_permission(request)