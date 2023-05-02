from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from telegram_bot.models import User


@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = User.objects.filter(id=request.user.id)
    if user.exists():
        user = user.first()

    if request.method == 'POST':

        if request.FILES:
            if request.FILES['profile_image'].size < (2 * 1024 * 1024):
                file = request.FILES['profile_image']
                default_storage.save(file.name, file)  # Save image to media/
                user.photo = file.name

        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')

        check_list = [username, email, old_password, new_password]

        if authenticate(request, username=request.user.email, password=old_password) and '' not in check_list:
            user.email = email
            user.username = username
            user.set_password(new_password)
            user.save()

        else:
            return redirect('/profile/')

        return redirect('/accounts/login/')

    context = {
        'user': user,
    }

    return render(request, 'profile.html', context)