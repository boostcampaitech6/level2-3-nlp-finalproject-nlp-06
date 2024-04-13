from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
import uuid
from .serializers import NoticeSerializer

from django.contrib.auth.models import User
from users.models import Profile, Notice

@api_view(['GET'])
def apiOverview(request):
    api_urls = [
        {'POST': '/api/users/token/' ,'description': 'Get JWT token for user authentication'},
        {'POST': '/api/users/token/refresh/', 'description': 'Refresh JWT token for user authentication'},

        {'POST': '/api/username/notices/', 'description': 'Create a notice for a user'},
        {'GET': '/api/username/notices/', 'description': 'Get all notices for a user'},
        {'GET': '/api/notices/id/', 'description': 'Get a single notice for a user'},
        {'PATCH': '/api/notices/id/', 'description': 'Update a notice to read'},
        {'DELETE': '/api/notices/id/', 'description': 'Delete a notice'},
    ]
    return Response(api_urls)


class NoticeView(APIView):
    def post(self, request, username):
        user = User.objects.get(username=username)
        data = request.data

        notice = Notice.objects.create(
            receiver=user.profile,
            title=data.get('title'),
            text=data.get('text'),
            retrospective_id=uuid.UUID(data.get('retrospective_id'))
        )
        notice.save()

        return Response("success", status=201)

    def get(self, request, username):
        user = User.objects.get(username=username)
        notices = user.profile.notices.all()
        serializer = NoticeSerializer(notices, many=True)
        return Response(serializer.data)
    


class SingleNoticeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        notice = request.user.profile.notices.get(id=pk)
        serializer = NoticeSerializer(notice, many=False)
        return Response(serializer.data)

    def patch(self, request, pk):
        notice = request.user.profile.notices.get(id=pk)
        notice.is_read = True
        notice.save()
        
        return Response("success", status=201)
    
    def delete(self, request, pk):
        notice = request.user.profile.notices.get(id=pk)
        notice.delete()

        return Response("success", status=204)


