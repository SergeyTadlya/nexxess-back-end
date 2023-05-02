from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from .models import InstallationSettings
from .models import TelegramSettings
from .models import Authentication
from .models import User


@admin.register(TelegramSettings)
class TelegramSettingsAdmin(admin.ModelAdmin):
    list_display = ['bot_name', 'telegram_bot_token']


@admin.register(InstallationSettings)
class InstallationSettingsAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Authentication)
class AuthenticationAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'email', 'step']


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': (
            'b24_contact_id',
            'email',
            'password',
            'username',
            'photo',
            'telegram_id',
            'first_name',
            'last_name',
            'step',
            'activation_code',
            'google_auth',
            'last_login'
        )}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    list_display = ('email', 'username', 'is_staff', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(User, UserAdmin)

