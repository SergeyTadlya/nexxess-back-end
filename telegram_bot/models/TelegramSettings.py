from django.db import models


class TelegramSettings(models.Model):
    bot_name = models.CharField(verbose_name='Telegram bot name', unique=True, max_length=50)
    telegram_bot_token = models.CharField(verbose_name='Telegram bot token', unique=True, max_length=100)
    api_url = models.CharField(verbose_name='Telegram api url', max_length=100, blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Is active', default=False, null=True)

    def __str__(self):
        return self.bot_name

    class Meta:
        verbose_name = 'Telegram bot settings'
        verbose_name_plural = 'Telegram bots settings'


class InstallationSettings(models.Model):
    title = models.CharField(verbose_name='Title', unique=True, max_length=20)
    domain = models.CharField(verbose_name='Domain', unique=True, max_length=50)
    is_active = models.BooleanField(verbose_name='Is active', default=False, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Installation settings'
        verbose_name_plural = 'Installation settings'
