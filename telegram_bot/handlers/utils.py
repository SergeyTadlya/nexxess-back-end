from ..models import User, Authentication
from api.views.Auth import UserAPICreate


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


def authorize_user(data):
    telegram_id = data['from']['id']

    unauthorized_user = Authentication.objects.filter(telegram_id=telegram_id)
    if unauthorized_user.exists():
        unauthorized_user = unauthorized_user.first()
        unauthorized_user.delete()

    user_api = UserAPICreate()
    user_api.post(email=unauthorized_user.email,
                  name=data['from']['username'] if data['from']['username'] else 'No username',
                  telegram_id=telegram_id,
                  first_name=data['from']['first_name'] if data['from']['first_name'] else 'No name',
                  last_name=data['from']['last_name'] if data['from']['last_name'] else 'No last name',
                  is_staff=False,
                  password=unauthorized_user.password)
