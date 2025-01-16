# silenttrinity/silenttrinity/teamserver/core/utils/decorators.py

from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

def require_auth(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return f(request, *args, **kwargs)
    return decorated_function

def require_teamserver_admin(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied('Admin privileges required')
        return f(request, *args, **kwargs)
    return decorated_function