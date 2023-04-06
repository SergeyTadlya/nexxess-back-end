from django.db import models
from django.contrib.auth.models import User


class Invoice(models.Model):
    manager = models.ForeignKey(User, verbose_name='Manager', on_delete=models.DO_NOTHING)
    invoice = models.JSONField(verbose_name='Invoice', blank=True, default=list)
    is_opened = models.BooleanField(verbose_name="Opened (yes/no)", default=False, null=True)
    created_at = models.DateTimeField(verbose_name='Create date', auto_now_add=True)

    def __str__(self):
        return f'Invoice, responsible - {self.manager}'

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
