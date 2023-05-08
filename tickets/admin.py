from django.contrib import admin
from .models import Ticket, Ticket_comments


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_id', 'responsible','ticket_title', 'ticket_text', 'is_opened',  'created_at', 'is_active']
    list_filter = ['responsible', 'is_opened']


@admin.register(Ticket_comments)
class Ticket_CommentsAdmin(admin.ModelAdmin):
    list_display = ['comment_id', 'ticket', 'text', 'manager_name', 'created_date','is_active']
    list_filter = ['ticket', 'is_active']
