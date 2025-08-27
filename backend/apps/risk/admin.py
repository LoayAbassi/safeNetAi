from django.contrib import admin
from .models import Account, ClientProfile, RiskEvent, Rule, Threshold

class AccountAdmin(admin.ModelAdmin):
    list_display = ('iban', 'owner', 'balance')
    # autocomplete_fields = ['owner']
    search_fields = ['owner__user__username'] 

admin.site.register(Account, AccountAdmin)
admin.site.register(ClientProfile)
admin.site.register(RiskEvent)
admin.site.register(Rule)
admin.site.register(Threshold)