"""User serializers."""

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        """Serializer metadata."""

        model = User
        fields = ['id', 'name', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
