from django.contrib import admin
from .models import Invoice, Task, B24keys

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_id', 'responsible', 'is_opened']
    list_filter = ['responsible', 'is_opened']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_id', 'responsible', 'is_opened']
    list_filter = ['responsible', 'is_opened']


@admin.register(B24keys)      # register in admin panel b24 keys
class B24keysAdmin(admin.ModelAdmin):
    list_display = ['id']

