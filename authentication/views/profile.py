from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render, redirect

from telegram_bot.models import User


@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = User.objects.filter(id=request.user.id)
    if user.exists():
        user = user.first()

    context = {'user': user}

    return render(request, 'profile.html', context)
