from django.db import models

# Create your models here.
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
    status = models.CharField(max_length=50, verbose_name='Status', blank=True, null=True)
    date = models.CharField(max_length=50, verbose_name='Date', blank=True, null=True)
    due_date = models.CharField(max_length=50, verbose_name='Due date', blank=True, null=True)

    def __str__(self):
        return f'Invoice {self.invoice_id}, responsible - {self.responsible}'

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'