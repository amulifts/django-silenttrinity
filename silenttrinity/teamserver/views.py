from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import TeamServerUser, AuthToken, LoginAttempt
from .core.utils.decorators import require_auth, require_teamserver_admin
import json
import hmac
import hashlib
from datetime import timedelta

@csrf_exempt
def register(request):
    """
    Register a new TeamServer user
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)
            
        # Create password hash using HMAC-SHA256
        password_hash = hmac.new(
            password.encode(),
            username.encode(),
            hashlib.sha256
        ).hexdigest()
        
        user = TeamServerUser.objects.create_user(
            username=username,
            password=password_hash
        )
        
        return JsonResponse({
            'message': 'User registered successfully',
            'user_id': str(user.id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
        
@csrf_exempt
def login(request):
    """
    Authenticate user and return auth token
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)
            
        # Record login attempt
        LoginAttempt.objects.create(
            username=username,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        user = authenticate(request, username=username, password=password)
        if not user:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
        # Create auth token
        token = AuthToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        return JsonResponse({
            'token': str(token.token),
            'expires_at': token.expires_at.isoformat(),
            'user_id': str(user.id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
@csrf_exempt
@require_auth
def logout(request):
    """
    Invalidate the current auth token
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({'error': 'No authorization token provided'}, status=401)
        
    try:
        auth_type, token = auth_header.split(' ', 1)
        if auth_type.lower() != 'bearer':
            return JsonResponse({'error': 'Invalid authorization type'}, status=401)
            
        # Invalidate token
        AuthToken.objects.filter(token=token).update(is_valid=False)
        
        return JsonResponse({'message': 'Logged out successfully'})
        
    except ValueError:
        return JsonResponse({'error': 'Invalid authorization header'}, status=401)
        
@require_auth
def user_info(request):
    """
    Get current user information
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    user = request.user
    return JsonResponse({
        'id': str(user.id),
        'username': user.username,
        'is_admin': user.is_teamserver_admin,
        'last_login': user.last_login_time.isoformat() if user.last_login_time else None,
        'last_ip': user.last_login_ip
    })
    
@require_teamserver_admin
def list_users(request):
    """
    List all TeamServer users (admin only)
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    users = TeamServerUser.objects.all()
    user_list = [{
        'id': str(user.id),
        'username': user.username,
        'is_admin': user.is_teamserver_admin,
        'last_login': user.last_login_time.isoformat() if user.last_login_time else None,
        'last_ip': user.last_login_ip
    } for user in users]
    
    return JsonResponse({'users': user_list})