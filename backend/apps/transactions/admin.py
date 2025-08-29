from django.contrib import admin
from .models import Transaction, FraudAlert

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('client', 'amount', 'transaction_type', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('client__full_name', 'client__national_id')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('client', 'amount', 'transaction_type')
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )

@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'risk_level', 'status', 'created_at')
    list_filter = ('risk_level', 'status', 'created_at')
    search_fields = ('transaction__client__full_name', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Alert Details', {
            'fields': ('transaction', 'risk_level', 'message', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
