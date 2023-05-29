from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy

from authentication.forms import *

from telegram_bot.models import User

from random import randint

import string
import random



def google_login(request):
    code = str(randint(100000, 999999))
    if request.user.id:
        user_email = request.user.email
    else:
        user_email = request.session._session.get('socialaccount_sociallogin').get('user').get('email')
    user = User.objects.filter(email=user_email)
    if user.exists():
        user = user.first()
        user.activation_code = code
        user.save()
        raw_password = user.password
        if len(raw_password) == 41:
            extra_text = f'Your one-time password for "{request.user.email}":\n{raw_password}\n You can change it in your profile.'
        else:
            extra_text = ''

    send_mail('Secret key',
                f'Your private key for "{request.user.email}":\n{code}\n{extra_text}',
                'cutrys69@gmail.com',
                [user_email],
                fail_silently=False)

    next_url = request.GET.get('next', reverse_lazy('authentication:verification'))

    return redirect(next_url)
