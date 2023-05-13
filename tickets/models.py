from django.db import models
from django.utils import timezone


class Ticket(models.Model):
    responsible = models.CharField(max_length=150, verbose_name='Responsible bitrix ID', blank=True, null=True)
    task_id = models.JSONField(max_length=50, verbose_name='TASK_ID', blank=True, null=True)
    ticket_title = models.CharField(max_length=25,  verbose_name='Ticket title', blank=True, null=True)
    ticket_text = models.TextField(verbose_name='Ticket description', max_length=1200, blank=True, null=True)
    status = models.CharField(max_length=500, verbose_name='Status', blank=True, null=True)
    is_opened = models.BooleanField(verbose_name="Opened (yes/no)", default=False, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    updated_time = models.CharField(max_length=500, blank=True, null=True)
    deadline = models.DateTimeField(verbose_name='Deadline', blank=True, null=True)
    b24_domain = models.CharField(max_length=200, blank=True, null=True)
    b24_member_id = models.CharField(max_length=500, blank=True, null=True)
    b24_application_token = models.CharField(max_length=500, blank=True, null=True)
    b24_time = models.CharField(max_length=200, blank=True, null=True)
    task_info = models.JSONField(verbose_name='TASK_INFO_DATA', default=list, blank=True, null=True)
    task_info_crm = models.JSONField(verbose_name='TASK_INFO_DATA_CRM', default=list, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Create date', auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'Ticket {self.task_id}, responsible - {self.responsible}'

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'


class TicketComments(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    comment_id = models.PositiveIntegerField()
    manager_name = models.CharField(max_length=50)
    added_documents = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField(verbose_name='Comment')
    is_opened = models.BooleanField()
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)


class TelegramTicket(models.Model):
    responsible = models.CharField(max_length=50, verbose_name='Responsible bitrix ID')
    title = models.CharField(verbose_name='Telegram ticket title', max_length=128)
    description = models.TextField(verbose_name='Telegram ticket description', max_length=1200, blank=True, null=True)

    def __str__(self):
        return f'Responsible - {self.responsible}'

    class Meta:
        verbose_name = 'Telegram ticket'
        verbose_name_plural = 'Telegram tickets'
