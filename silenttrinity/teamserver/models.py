from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class TeamServerUser(AbstractUser):
    """Custom user model for TeamServer"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Session(models.Model):
    """Model for tracking agent sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(TeamServerUser, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    os = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checkin = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

class SessionLog(models.Model):
    """Model for session activity logging"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class AuthToken(models.Model):
    """Model for API authentication tokens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(TeamServerUser, related_name='auth_tokens', on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)
    is_valid = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']