from django.contrib import admin
from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_id', 'responsible', 'is_opened']
    list_filter = ['responsible', 'is_opened']