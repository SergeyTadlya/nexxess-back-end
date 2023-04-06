from django.shortcuts import render, redirect
from authentication.forms import *
from allauth.account.views import SignupView


def logout_view(request):
    return render(request, 'logout.html')


def login_view(request):
    login_form = CustomLoginForm(request.POST)
    if login_form.is_valid():
        return redirect('/admin ')
    else:
        login_form = CustomLoginForm()
    context = {'login_form': CustomLoginForm}
    return render(request, 'login.html', context)


class CustomSignupView(SignupView):
    form_class = CustomSignupForm
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs