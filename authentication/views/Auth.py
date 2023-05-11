from django.contrib.auth.decorators import login_required
from allauth.account.views import LoginView, SignupView, LogoutView, _ajax_response
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.urls import reverse_lazy

from authentication.forms import *
from telegram_bot.models import User
from random import randint


def verification(request):
    if request.user.is_authenticated:
        user = User.objects.filter(email=request.user.email)
        if user.exists():
            user = user.first()

        verify_code = request.GET.get('verify_code') if request.GET.get('verify_code') else ''
        if user.activation_code == verify_code:
            user.google_auth = True
            user.save()
            return redirect('/')
        return render(request, '2fa.html')
    else:

        return render(request, 'main.html')


class MyLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                next_url = self.request.GET.get('next', reverse_lazy('authentication:main'))
                return redirect(next_url)

            try:
                code = randint(100000, 999999)
                user = User.objects.filter(email=self.request.user.email)
                if user.exists():
                    user = user.first()
                    user.activation_code = code
                    user.save()
                send_mail('Secret key',
                          f'Your private key for "{self.request.user.email}":\n{code}',
                          'cutrys69@gmail.com',
                          [self.request.user.email],
                          fail_silently=False)

            except Exception as e:
                print(e)
            if self.request.user.google_auth:
                next_url = self.request.GET.get('next', reverse_lazy('authentication:main'))
            elif self.request.user.google_auth == False:
                next_url = self.request.GET.get('next', reverse_lazy('authentication:verification'))
            return redirect(next_url)
        else:
            return response


class MyLogoutView(LogoutView):

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            user = User.objects.filter(email=self.request.user.email)
            if user.exists():
                user = user.first()
                user.google_auth = False
                user.save()
                self.logout()

        response = redirect('/')

        return _ajax_response(self.request, response)


class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


@login_required(login_url='/accounts/login/')
def edit_profile(request):
    if request.method == 'POST':

        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})
