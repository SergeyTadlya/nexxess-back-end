from django.contrib import admin
from .models import Invoice, Status, StripeSettings, LocalInvoice, RightSignatureSettings, RightSignatureTemplate, \
    RightSignatureDocument, RightSignatureField


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_id', 'responsible', 'status']
    list_filter = ['responsible']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['abbreviation', 'value', 'color']

@admin.register(StripeSettings)
class StripeSettingsAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(LocalInvoice)
class LocalInvoiceAdmin(admin.ModelAdmin):
    list_display = ['b24_invoice_id', 'stripe_price_id']


@admin.register(RightSignatureTemplate)
class RightSignatureTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'reference_id', 'is_active']


@admin.register(RightSignatureDocument)
class RightSignatureDocumentAdmin(admin.ModelAdmin):
    list_display = ['reference_id', 'template', 'status', 'contact', 'invoice', 'created_at', 'updated_at']


@admin.register(RightSignatureSettings)
class RightSignatureSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active']


@admin.register(RightSignatureField)
class RightSignatureFieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference_id', 'template', 'name', 'value']
