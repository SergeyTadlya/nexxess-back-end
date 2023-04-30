from django.db import models



class Service(models.Model):
    title = models.CharField(max_length=255, verbose_name='Name')
    service_id = models.CharField(max_length=50, unique=True)
    title_description = models.TextField(verbose_name='Description')
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

# Create your models here.
