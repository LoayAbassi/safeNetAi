from django.contrib import admin
from .models import Rule, Threshold

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