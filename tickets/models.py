from django.db import models
from django.utils import timezone



class Ticket(models.Model):
    responsible = models.CharField(max_length=150, verbose_name='Responsible bitrix ID')
    task_id = models.JSONField(max_length=50, verbose_name='TASK_ID')
    ticket_title = models.CharField(max_length=25,  verbose_name='Ticket title', blank=True)
    b24_domain = models.CharField(max_length=200)
    b24_member_id = models.CharField(max_length=500)
    b24_application_token = models.CharField(max_length=500)
    b24_time = models.CharField(max_length=200)
    deadline = models.DateTimeField(verbose_name='Deadline', blank=True, null=True)
    status = models.CharField(max_length=500, verbose_name='Status', blank=True)
    ticket_text = models.TextField(verbose_name='Ticket description', blank=True, max_length=1200)
    task_info = models.JSONField(verbose_name='TASK_INFO_DATA', blank=True, default=list)
    task_info_crm = models.JSONField(verbose_name='TASK_INFO_DATA_CRM', blank=True, default=list)
    is_opened = models.BooleanField(verbose_name="Opened (yes/no)", default=False, null=True)
    created_at = models.DateTimeField(verbose_name='Create date', auto_now_add=True, blank=True)
    updated_time = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Ticket {self.task_id}, responsible - {self.responsible}'

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'




class Ticket_comments(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    comment_id = models.PositiveIntegerField()
    text = models.TextField(verbose_name='Comment')
    created_date = models.DateTimeField(default=timezone.now)
    manager_name = models.CharField(max_length=50)
    is_opened = models.BooleanField()
    added_documents = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
