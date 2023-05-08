from django.db import models
from django.contrib.auth.models import User


class B24keys(models.Model):     ## create model for save and edit keys,  which must be protect from others
    # ng_link = models.CharField(max_length=200, verbose_name='ngrok link')
    b24_webhook = models.CharField(max_length=200, verbose_name='Bitrix24 webhook')
    domain = models.CharField(max_length=200, verbose_name='B24 domain', blank=True)
    rest_key = models.CharField(max_length=200, verbose_name='B24 rest_key', blank=True)

    class Meta:
        verbose_name_plural = 'B24 key'
