from django.db import models


class Status(models.Model):
    abbreviation = models.CharField(verbose_name='Abbreviation', max_length=10)
    value = models.CharField(verbose_name='Value', max_length=10)
    color = models.CharField(verbose_name='Color', max_length=20)

    def __str__(self):
        return f'{self.abbreviation} - {self.value}'

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'


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
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name='Status', blank=True, null=True)
    date = models.DateTimeField(verbose_name='Date', blank=True, null=True)
    due_date = models.DateTimeField(verbose_name='Due date', blank=True, null=True)

    def __str__(self):
        return f'Invoice {self.invoice_id}, responsible - {self.responsible}'

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
