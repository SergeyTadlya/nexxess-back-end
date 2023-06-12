from django.http import HttpResponse

from ..models import TelegramSettings, InstallationSettings

import requests


def set_telegram_webhook(request):
    telegram_settings = TelegramSettings.objects.filter(is_active=True)
    install_settings = InstallationSettings.objects.filter(is_active=True)

    if telegram_settings.exists() and install_settings.exists():
        telegram_settings = telegram_settings.first()
        install_settings = install_settings.first()

        webhook_url = f'{telegram_settings.api_url}bot{telegram_settings.telegram_bot_token}/setWebhook?url={install_settings.domain}'
        webhook_url += 'telegram/' if install_settings.domain[-1] == '/' else '/telegram/'

        response = requests.post(url=webhook_url)
        data = response.json()
        description = data['description'] if data['ok'] else 'Something went wrong'

        return HttpResponse(description, content_type='application/json')
