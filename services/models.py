from django.db import models


class Service(models.Model):
    category = models.ForeignKey(
        to='services.ServiceCategory',
        verbose_name='Category',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255, verbose_name='Name')
    service_id = models.CharField(max_length=50, unique=True)
    # title_description ##= models.TextField(verbose_name='Description')
    preview_text = models.CharField(verbose_name='Preview text', max_length=100, null=True, blank=True)
    detail_text = models.CharField(verbose_name='Detail text', max_length=3000, null=True, blank=True)
    price = models.DecimalField(verbose_name='Price', max_digits=10, decimal_places=2)
    description_parts = models.TextField(verbose_name='Description parts', blank=True, null=True),
    image = models.ImageField(upload_to='services', verbose_name='Image', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    currency = models.CharField(max_length=12)
    stripe_id = models.CharField(verbose_name='Stripe product id', max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'


class ServiceCategory(models.Model):
    category_b24_id = models.CharField(verbose_name="B24 category id", max_length=10)
    category_name = models.CharField(verbose_name='Category name', max_length=150)

    def __str__(self):
        return f'Category {self.category_name}'

    class Meta:
        verbose_name = 'Service category'
        verbose_name_plural = 'Service categories'
