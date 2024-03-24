from rest_framework import serializers
from users.models import Profile, Notice


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
        depth = 1