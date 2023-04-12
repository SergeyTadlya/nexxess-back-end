from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_id', 'responsible', 'is_opened']
    list_filter = ['responsible', 'is_opened']
