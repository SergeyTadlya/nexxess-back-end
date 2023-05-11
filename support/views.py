from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required(login_url='/accounts/login/')
def support(request):
    if request.user.is_authenticated and request.user.google_auth or request.user.is_superuser:
        return render(request, "support/support.html")
    else: return redirect('authentication:main')
