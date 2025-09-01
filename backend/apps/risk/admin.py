from django.contrib import admin
from .models import ClientProfile, Rule, Threshold

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'national_id', 'bank_account_number', 'balance', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('first_name', 'last_name', 'national_id', 'bank_account_number', 'user__email')
    readonly_fields = ('bank_account_number', 'avg_amount', 'std_amount', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'national_id')
        }),
        ('Financial Information', {
            'fields': ('balance', 'avg_amount', 'std_amount')
        }),
        ('Location Information', {
            'fields': ('home_lat', 'home_lng', 'last_known_lat', 'last_known_lng'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('bank_account_number', 'user', 'device_fingerprint'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make first_name, last_name, and national_id required
        for field_name in ['first_name', 'last_name', 'national_id']:
            if field_name in form.base_fields:
                form.base_fields[field_name].required = True
        return form

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'enabled')
    list_filter = ('enabled',)
    search_fields = ('key', 'description')
    ordering = ('key',)
    
    fieldsets = (
        ('Rule Information', {
            'fields': ('key', 'description', 'enabled')
        }),
        ('Parameters', {
            'fields': ('params_json',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Threshold)
class ThresholdAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key', 'description')
    ordering = ('key',)
    
    fieldsets = (
        ('Threshold Information', {
            'fields': ('key', 'value', 'description')
        }),
    )