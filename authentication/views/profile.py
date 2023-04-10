from django.shortcuts import render, redirect
from authentication.forms import *
from allauth.account.views import SignupView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm


@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserChangeForm(instance=user)

    context = {
        'form': form
    }

    return render(request, 'profile.html', context)