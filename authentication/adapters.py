from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from telegram_bot.models import User


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        user = User.objects.filter(email=sociallogin.user.email)
        if user and not sociallogin.user.id:  # якщо існує юзер без соціального акаунту
            request.user = sociallogin.user
            user_email = sociallogin.user.email
            user = User.objects.filter(email=user_email)
            user = user.first()
            user.save()
            sociallogin.connect(sociallogin, user)  # прив'язка соціального акаунту до існуючого юзера
        
        if sociallogin.account.provider == 'google':  # якщо соціальний акаунт прив'язан до юзера
            sociallogin.state['next'] = '/accounts/googlelogin/'
