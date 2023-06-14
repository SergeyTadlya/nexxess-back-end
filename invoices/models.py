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
    service_id = models.CharField(max_length=50)
    invoice_info = models.JSONField(verbose_name='Data', blank=True, default=list)
    price = models.DecimalField(verbose_name='Price', max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Create date', auto_now_add=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name='Status', blank=True, null=True)
    date = models.DateTimeField(verbose_name='Date', blank=True, null=True)
    due_date = models.DateTimeField(verbose_name='Due date', blank=True, null=True)
    product_title = models.CharField(verbose_name='Product title', max_length=200, blank=True, null=True)
    task_created = models.BooleanField(verbose_name='Task created', default=False)
    time_remaining = models.CharField(verbose_name='Bought time',max_length=200, blank=True, null=True)
    tracked_time = models.CharField(verbose_name='Tracked time', blank=True, null=True, max_length=100)

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
    telegram_provider_token = models.CharField(verbose_name='Telegram Provider token', max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Stripe - {self.name}'

    class Meta:
        verbose_name = 'Stripe settings'
        verbose_name_plural = 'Stripe settings'


class LocalInvoice(models.Model):
    b24_invoice_id = models.CharField(verbose_name='Bitrix24 invoice id', max_length=10)
    stripe_price_id = models.CharField(verbose_name='Stripe id', max_length=100)
    payment_link = models.CharField(verbose_name='Payment link', max_length=250, null=True, blank=True)


class ShareFileSettings(models.Model):
    name = models.CharField(verbose_name="Name", max_length=50, unique=True)
    subdomain = models.CharField(verbose_name="Subdomain", max_length=50)
    client_id = models.CharField(verbose_name="Client ID", max_length=100, unique=True)
    client_secret = models.CharField(verbose_name="Client Secret", max_length=100, unique=True)
    redirect_uri = models.CharField(verbose_name="Redirect Uri", max_length=100, null=True, blank=True)
    code = models.CharField(verbose_name="Code", max_length=50, null=True, blank=True)
    username = models.CharField(verbose_name="Username", max_length=50, null=True, blank=True)
    password = models.CharField(verbose_name="Password", max_length=50, null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Is active', default=False)

    def __str__(self):
        return f'ShareFile setting - {self.name}'

    class Meta:
        verbose_name = 'ShareFile settings'
        verbose_name_plural = 'ShareFile settings'


class RightSignatureSettings(models.Model):
    name = models.CharField(verbose_name="Name", max_length=50, unique=True)
    client_id = models.CharField(verbose_name="Client ID", max_length=100, unique=True)
    client_secret = models.CharField(verbose_name="Client Secret", max_length=100, unique=True)
    private_api = models.CharField(verbose_name="Private API", max_length=100, null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Is active', default=False)

    def __str__(self):
        return f'RightSignature setting - {self.name}'

    class Meta:
        verbose_name = 'RightSignature settings'
        verbose_name_plural = 'RightSignature settings'


class RightSignatureTemplate(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100, unique=True)
    reference_id = models.CharField(verbose_name="Reference ID", max_length=100, unique=True)
    is_active = models.BooleanField(verbose_name='Is active', default=False)

    def __str__(self):
        return f'RightSignature template - {self.name}'

    class Meta:
        verbose_name = 'RightSignature template'
        verbose_name_plural = 'RightSignature templates'


class RightSignatureDocument(models.Model):
    reference_id = models.CharField(verbose_name="Reference ID", max_length=100, unique=True)
    template = models.ForeignKey(to="RightSignatureTemplate", on_delete=models.PROTECT, verbose_name='Template')
    contact = models.ForeignKey(to="telegram_bot.User", on_delete=models.PROTECT, verbose_name='Contact')
    invoice = models.ForeignKey(to="Invoice", on_delete=models.PROTECT, verbose_name='Invoice')
    status = models.CharField(verbose_name='Status', max_length=50)
    created_at = models.DateTimeField(verbose_name='Create date', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Update date', auto_now=True)

    def __str__(self):
        return f'RightSignature document - {self.id}'

    class Meta:
        verbose_name = 'RightSignature document'
        verbose_name_plural = 'RightSignature documents'


class RightSignatureField(models.Model):
    reference_id = models.CharField(verbose_name="Reference ID", max_length=100, unique=True, null=True, blank=True)
    template = models.ForeignKey(to="RightSignatureTemplate", on_delete=models.PROTECT, verbose_name='Template')
    name = models.CharField(verbose_name="Name", max_length=100, unique=True)
    value = models.CharField(verbose_name="Value", max_length=100, null=True, blank=True)

    def __str__(self):
        return f'RightSignature field - {self.id}'

    class Meta:
        verbose_name = 'RightSignature field'
        verbose_name_plural = 'RightSignature fields'
