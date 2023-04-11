from django.db import models
from django.contrib.auth.models import User


class Invoice(models.Model):
    responsible = models.CharField(max_length=150, verbose_name='Responsible')
    invoice_id = models.CharField(max_length=50)
    b24_domain = models.CharField(max_length=200)
    b24_member_id = models.CharField(max_length=500)
    b24_application_token = models.CharField(max_length=500)
    b24_time = models.CharField(max_length=200)
    invoice_info = models.JSONField(verbose_name='Data', blank=True, default=list)
    is_opened = models.BooleanField(verbose_name="Opened (yes/no)", default=False, null=True)
    price = models.DecimalField(verbose_name='Price', max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Create date', auto_now_add=True)

    def __str__(self):
        return f'Invoice {self.invoice_id}, responsible - {self.manager}'

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'


class Task(models.Model):
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
        return f'Task {self.task_id}, responsible - {self.manager}'

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class B24keys(models.Model):     ## create model for save and edit keys,  which must be protect from others
    # ng_link = models.CharField(max_length=200, verbose_name='ngrok link')
    b24_webhook = models.CharField(max_length=200, verbose_name='Bitrix24 webhook')

    class Meta:
        verbose_name_plural = 'Server settings'