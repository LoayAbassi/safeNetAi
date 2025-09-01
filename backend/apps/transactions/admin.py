from django.contrib import admin
from .models import Transaction, FraudAlert, TransactionOTP

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('client', 'amount', 'transaction_type', 'status', 'risk_score', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('client__full_name', 'client__bank_account_number')
    readonly_fields = ('created_at', 'updated_at', 'risk_score')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('client', 'amount', 'transaction_type', 'status', 'risk_score')
        }),
        ('Transfer Information', {
            'fields': ('to_account_number', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'risk_score', 'level', 'status', 'created_at')
    list_filter = ('level', 'status', 'created_at')
    search_fields = ('transaction__client__full_name', 'transaction__client__bank_account_number')
    readonly_fields = ('transaction', 'risk_score', 'level', 'triggers', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('transaction', 'risk_score', 'level', 'status')
        }),
        ('Details', {
            'fields': ('triggers',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Fraud alerts should only be created programmatically

@admin.register(TransactionOTP)
class TransactionOTPAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'user', 'otp', 'expires_at', 'used', 'attempts')
    list_filter = ('used', 'created_at')
    search_fields = ('transaction__id', 'user__email')
    readonly_fields = ('transaction', 'user', 'otp', 'created_at', 'expires_at', 'used', 'attempts')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('transaction', 'user', 'otp')
        }),
        ('Status', {
            'fields': ('used', 'attempts')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # OTPs should only be created programmatically
