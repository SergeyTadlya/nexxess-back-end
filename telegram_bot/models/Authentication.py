from django.db import models


class Authentication(models.Model):
    telegram_id = models.PositiveIntegerField(verbose_name='Telegram user ID', null=True, blank=True)
    email = models.CharField(verbose_name='User e-mail', max_length=64, null=True, blank=True)
    verify_code = models.CharField(verbose_name='User verify code', max_length=64, null=True, blank=True)
    step = models.CharField(verbose_name='User step', max_length=128, null=True, blank=True)

    def __str__(self):
        return f'{self.telegram_id}'

    class Meta:
        verbose_name = 'Authentication'
        verbose_name_plural = 'Authentications'
