# silenttrinity/silenttrinity/teamserver/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import TeamServerUser, AuthToken, Session, SessionLog

@admin.register(TeamServerUser)
class TeamServerUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'created_at')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),  # 'last_login' is built-in
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    # readonly_fields = () # no 'api_token' unless you add that to TeamServerUser


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    # Drop references to non-existent fields
    list_display = ('hostname', 'username', 'os', 'last_checkin', 'active')
    list_filter = ('active', 'os')
    search_fields = ('hostname', 'username', 'os')


@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ('session', 'type', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('session__hostname', 'content')

@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_valid')
    list_filter = ('is_valid', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('token',)
