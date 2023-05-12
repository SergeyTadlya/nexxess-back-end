from django.db import models


class Status(models.Model):
    abbreviation = models.CharField(verbose_name='Abbreviation', max_length=10)
    value = models.CharField(verbose_name='Value', max_length=10)
    color = models.CharField(verbose_name='Color', max_length=20)
    sticker = models.CharField(verbose_name='Sticker', max_length=8)

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
    product_title = models.CharField(verbose_name='Product title', max_length=200, blank=True, null=True)

    def __str__(self):
        return f'Invoice {self.invoice_id}, responsible - {self.responsible}'

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'


class StripeSettings(models.Model):
    name = models.CharField(verbose_name="Name", max_length=20, unique=True)
    publishable_key = models.CharField(verbose_name="Publishable key", max_length=250, unique=True)
    secret_key = models.CharField(verbose_name="Secret key", max_length=250, unique=True)
    webhook_url = models.CharField(verbose_name='Webhook url', max_length=250, null=True, blank=True)

    def __str__(self):
        return f'Stripe - {self.name}'

    class Meta:
        verbose_name = 'Stripe settings'
        verbose_name_plural = 'Stripe settings'


class LocalInvoice(models.Model):
    b24_invoice_id = models.CharField(verbose_name='Bitrix24 invoice id', max_length=10)
    stripe_price_id = models.CharField(verbose_name='Stripe id', max_length=100)
    payment_link = models.CharField(verbose_name='Payment link', max_length=250, null=True, blank=True)
