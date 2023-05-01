from django.contrib import admin
from .models import Invoice, Status, StripeSettings, LocalInvoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_id', 'responsible', 'status', 'is_opened']
    list_filter = ['responsible', 'is_opened']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['abbreviation', 'value', 'color']

@admin.register(StripeSettings)
class StripeSettingsAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(LocalInvoice)
class LocalInvoiceAdmin(admin.ModelAdmin):
    list_display = ['b24_invoice_id', 'stripe_price_id']
