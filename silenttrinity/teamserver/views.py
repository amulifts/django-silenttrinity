from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
import json
import uuid

from .models import TeamServerUser, Session, AuthToken
from .core.utils.decorators import require_auth, require_teamserver_admin

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """Handle user login"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)
            
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
        login(request, user)
        
        # Create auth token
        token = AuthToken.objects.create(
            user=user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timezone.timedelta(days=1)
        )
        
        return JsonResponse({
            'token': token.token,
            'user_id': str(user.id),
            'username': user.username
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def logout_view(request):
    """Handle user logout"""
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})

@require_http_methods(["GET"])
@require_auth
def sessions_view(request):
    """Get list of active sessions"""
    sessions = Session.objects.filter(active=True)
    return JsonResponse({
        'sessions': [{
            'id': str(session.id),
            'hostname': session.hostname,
            'username': session.username,
            'os': session.os,
            'last_checkin': session.last_checkin.isoformat(),
            'created_at': session.created_at.isoformat()
        } for session in sessions]
    })

@require_http_methods(["GET"])
@require_teamserver_admin
def users_view(request):
    """Get list of users (admin only)"""
    users = TeamServerUser.objects.all()
    return JsonResponse({
        'users': [{
            'id': str(user.id),
            'username': user.username,
            'is_staff': user.is_staff,
            'created_at': user.created_at.isoformat()
        } for user in users]
    })