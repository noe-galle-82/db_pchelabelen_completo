from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets

from .serializers import UserSerializer

# Create your views here.

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    groups = [g.name for g in user.groups.all()]
    return Response({
        "id": user.id,
        "username": user.username,
        "role": groups[0] if groups else None,
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.all()
    users_data = []
    
    for user in users:
        groups = [g.name for g in user.groups.all()]
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": groups[0] if groups else None,
        })
    
    return Response(users_data)


# ViewSet para operaciones CRUD completas de usuarios
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
