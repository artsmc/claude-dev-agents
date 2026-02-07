"""User views."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent users."""
        recent_users = User.objects.all()[:10]
        serializer = self.get_serializer(recent_users, many=True)
        return Response(serializer.data)
