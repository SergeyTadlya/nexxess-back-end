from ..models import TelegramSettings, InstallationSettings
from django.http import HttpResponse

import requests


def set_telegram_webhook(request):
    active_telegram_settings = TelegramSettings.objects.filter(is_active=True)
    active_install_settings = InstallationSettings.objects.filter(is_active=True)

    if active_telegram_settings.exists() and active_install_settings.exists():
        active_telegram_settings = active_telegram_settings.first()
        active_install_settings = active_install_settings.first()

        webhook_url = active_telegram_settings.api_url + 'bot' + active_telegram_settings.telegram_bot_token + \
                      '/setWebhook?url=' + active_install_settings.domain
        webhook_url += 'telegram/' if active_install_settings.domain[-1] == '/' else '/telegram/'

        response = requests.post(url=webhook_url)
        data = response.json()
        description = data['description'] if data['ok'] else 'Something went wrong'

        return HttpResponse(description, content_type='application/json')
