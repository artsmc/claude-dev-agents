"""User models."""

from django.db import models


class User(models.Model):
    """User model."""

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata."""

        ordering = ['-created_at']
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        """String representation."""
        return self.name
