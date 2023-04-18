from ..models import InstallationSettings, TelegramSettings


class SettingsHelper:
    @staticmethod
    def get_url(type: str) -> str:
        main_settings = InstallationSettings.objects.filter(is_active=True)

        if main_settings.exists():
            main_settings = main_settings.first()

            if type == 'api':
                main_settings.domain += '' if main_settings.domain[-1] == '/' else '/'
                return main_settings.domain + main_settings.api_url

            elif type == 'callback':
                main_settings.domain += '' if main_settings.domain[-1] == '/' else '/'
                return main_settings.domain + main_settings.api_url
        else:
            return 'URL not found'

    @staticmethod
    def get_bot_token() -> str:
        telegram_settings = TelegramSettings.objects.filter(is_active=True)

        if telegram_settings.exists():
            telegram_settings = telegram_settings.first()

            return telegram_settings.telegram_bot_token
