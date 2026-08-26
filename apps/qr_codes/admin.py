from django.contrib import admin
from .models import QRCodeSession


@admin.register(QRCodeSession)
class QRCodeSessionAdmin(admin.ModelAdmin):
    list_display = ['lecture', 'token_short', 'is_active', 'expires_at', 'regeneration_count']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['token', 'secret_key', 'created_at', 'expires_at']
    raw_id_fields = ['lecture']

    def token_short(self, obj):
        return obj.token[:12] + '...' if len(obj.token) > 12 else obj.token
    token_short.short_description = 'Token'
