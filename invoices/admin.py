from django.contrib import admin
from .models import Invoice, Status


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_id', 'responsible', 'status', 'is_opened']
    list_filter = ['responsible', 'is_opened']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['abbreviation', 'value', 'color']
