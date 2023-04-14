from ..models import User, Authentication


def get_chat_id(data):
    chat_id = data['message']['chat']['id']

    return chat_id


def get_user(data):
    telegram_id = data['message']['from']['id']

    user = User.objects.filter(telegram_id=telegram_id)

    if user.exists():
        user = user.first()
        return user
    else:
        unauthorized_user = Authentication.objects.create(telegram_id=telegram_id)
        unauthorized_user.step = 'set_email'
        unauthorized_user.save()
        return None


def create_user(data):
    telegram_id = data['from']['id']

    unauthorized_user = Authentication.objects.filter(telegram_id=telegram_id)
    if unauthorized_user.exists():
        unauthorized_user = unauthorized_user.first()

    user = User()
    user.email = unauthorized_user.email
    user.name = data['from']['username'] if data['from']['username'] else 'No username'
    user.telegram_id = telegram_id
    user.first_name = data['from']['first_name'] if data['from']['first_name'] else 'No name'
    user.last_name = data['from']['last_name'] if data['from']['last_name'] else 'No last name'

    user.set_password(unauthorized_user.password)

    user.save()
