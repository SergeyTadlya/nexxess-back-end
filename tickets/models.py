from django.db import models


class Ticket(models.Model):
    responsible = models.CharField(max_length=150, verbose_name='Responsible')
    task_id = models.CharField(max_length=50)
    b24_domain = models.CharField(max_length=200)
    b24_member_id = models.CharField(max_length=500)
    b24_application_token = models.CharField(max_length=500)
    b24_time = models.CharField(max_length=200)
    task_info = models.JSONField(verbose_name='Data', blank=True, default=list)
    is_opened = models.BooleanField(verbose_name="Opened (yes/no)", default=False, null=True)
    created_at = models.DateTimeField(verbose_name='Create date', auto_now_add=True)

    def __str__(self):
        return f'Ticket {self.task_id}, responsible - {self.responsible}'

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
