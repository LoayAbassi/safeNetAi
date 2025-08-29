from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ClientProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'national_id', 'bank_account_number', 'balance', 'risk_score', 'user', 'created_at')
    list_filter = ('risk_score', 'created_at')
    search_fields = ('full_name', 'national_id', 'bank_account_number')
    readonly_fields = ('national_id', 'bank_account_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('full_name', 'national_id', 'bank_account_number')
        }),
        ('Financial Information', {
            'fields': ('balance', 'risk_score')
        }),
        ('User Account', {
            'fields': ('user',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
