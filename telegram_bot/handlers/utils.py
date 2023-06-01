from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from ..models import User, Authentication


def get_chat_id(data):
    return data['message']['chat']['id']


def get_user_step(data):
    user = User.objects.filter(telegram_id=data['message']['chat']['id'])

    return user.first().step if user.exists() else None


def get_user(data):
    telegram_id = data['message']['chat']['id']

    user = User.objects.filter(telegram_id=telegram_id)

    if user.exists() and user.first().telegram_is_authenticate:
        return user.first()
    else:
        unauthorized_user = Authentication.objects.filter(telegram_id=telegram_id)
        unauthorized_user = unauthorized_user.first() if unauthorized_user.exists() else Authentication.objects.create(telegram_id=telegram_id)

        unauthorized_user.step = 'SET_EMAIL'
        unauthorized_user.save()
        return unauthorized_user


def authorize_user(data):
    telegram_id = data['from']['id']

    unauthorized_user = Authentication.objects.filter(telegram_id=telegram_id)
    if unauthorized_user.exists():
        unauthorized_user = unauthorized_user.first()

    user = User.objects.filter(email=unauthorized_user.email)
    unauthorized_user.delete()
    if user.exists():
        user = user.first()

    try:
        user.telegram_id = telegram_id
        user.telegram_username = data['from']['username'] if 'username' in data['from'].keys() else ''
        user.telegram_first_name = data['from']['first_name'] if 'first_name' in data['from'].keys() else ''
        user.telegram_last_name = data['from']['last_name'] if 'last_name' in data['from'].keys() else ''
        user.telegram_is_authenticate = True
        user.step = ''
        user.save()
    except Exception as e:
        print(e)


class MyStyleCalendar(DetailedTelegramCalendar):
    prev_button = "⬅️"
    next_button = "➡️"

    middle_button_year = "➖"

    empty_nav_button = "🚫"
    empty_day_button = "➖"
    empty_month_button = "➖"

    size_year = 1
    size_year_column = 2


def format_price_for_service(price):
    price = str(price)
    price = price.rstrip('0').rstrip('.') if '.' in price else price

    return int(price) * 100
