from django.shortcuts import render, redirect
from authentication.forms import *
from allauth.account.views import SignupView
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

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



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authentication.forms import EditProfileForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})