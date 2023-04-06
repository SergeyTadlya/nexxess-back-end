from django.shortcuts import render, redirect


def services(request):
    return render(request, "services/services.html")