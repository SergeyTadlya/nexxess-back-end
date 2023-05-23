from django.db import models


class B24keys(models.Model):
    b24_webhook = models.CharField(max_length=200, verbose_name='Bitrix24 webhook')
    domain = models.CharField(max_length=200, verbose_name='B24 domain', blank=True)
    rest_key = models.CharField(max_length=200, verbose_name='B24 rest_key', blank=True)

    class Meta:
        verbose_name = "B24 key"
        verbose_name_plural = "B24's keys"
