from django.contrib import admin
from .models import Invoice, Task, WebhookTask, WebhookInvoice, B24keys

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_id', 'manager', 'is_opened']
    list_filter = ['manager']


@admin.register(WebhookTask)
class WebhookTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'entities_id', 'b24_domain', 'b24_time']
    list_filter = ['b24_domain']


@admin.register(WebhookInvoice)
class WebhookInvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'entities_id', 'b24_domain', 'b24_time']
    list_filter = ['b24_domain']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_id', 'manager', 'is_opened']
    list_filter = ['manager']


@admin.register(B24keys)      # register in admin panel b24 keys
class B24keysAdmin(admin.ModelAdmin):
    list_display = ['id']

