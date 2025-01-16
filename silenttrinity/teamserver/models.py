from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class TeamServerUser(AbstractUser):
    """
    Custom user model for TeamServer authentication
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_token = models.UUIDField(default=uuid.uuid4, unique=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_time = models.DateTimeField(default=timezone.now)
    is_teamserver_admin = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'teamserver_users'
        
class AuthToken(models.Model):
    """
    Authentication tokens for API access
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(TeamServerUser, on_delete=models.CASCADE, related_name='auth_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_valid = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True)
    last_used_ip = models.GenericIPAddressField(null=True)
    
    class Meta:
        db_table = 'teamserver_auth_tokens'
        
    def is_expired(self):
        return timezone.now() > self.expires_at
        
    def invalidate(self):
        self.is_valid = False
        self.save()
        
class LoginAttempt(models.Model):
    """
    Track login attempts for rate limiting and security
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'teamserver_login_attempts'

class Session(models.Model):
    """
    Active C2 sessions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(TeamServerUser, on_delete=models.CASCADE, related_name='sessions')
    name = models.CharField(max_length=50)
    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    operating_system = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    last_checkin = models.DateTimeField(auto_now=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')
    
    class Meta:
        db_table = 'teamserver_sessions'
        
class SessionLog(models.Model):
    """
    Logs for session activity
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50)  # command, response, error, etc.
    content = models.TextField()
    
    class Meta:
        db_table = 'teamserver_session_logs'