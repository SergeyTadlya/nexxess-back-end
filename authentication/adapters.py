from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from telegram_bot.models import User


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        user = User.objects.filter(email=sociallogin.user.email)
        if user and not sociallogin.user.id:  # if user is exist without social acc
            request.user = sociallogin.user
            user_email = sociallogin.user.email
            user = User.objects.filter(email=user_email)
            user = user.first()
            user.save()
            sociallogin.connect(sociallogin, user)  # add social acc to avaible acc in db
        if sociallogin.account.provider == 'google':  # socail acc attached
            sociallogin.state['next'] = '/accounts/googlelogin/'
