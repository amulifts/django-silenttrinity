from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import TeamServerUser, AuthToken, LoginAttempt, Session, SessionLog

@admin.register(TeamServerUser)
class TeamServerUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_teamserver_admin', 'last_login_time', 'last_login_ip')
    list_filter = ('is_teamserver_admin', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('TeamServer info', {'fields': ('api_token', 'is_teamserver_admin')}),
        ('Important dates', {'fields': ('last_login_time', 'date_joined')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    readonly_fields = ('api_token',)

@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_valid', 'last_used_at')
    list_filter = ('is_valid', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('token',)

@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'ip_address', 'timestamp', 'success')
    list_filter = ('success', 'timestamp')
    search_fields = ('username', 'ip_address')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'hostname', 'username', 'ip_address', 'status', 'last_checkin')
    list_filter = ('status', 'operating_system')
    search_fields = ('name', 'hostname', 'username', 'ip_address')

@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ('session', 'timestamp', 'type')
    list_filter = ('type', 'timestamp')
    search_fields = ('session__name', 'content')