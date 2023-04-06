from django.shortcuts import render, redirect


def support(request):
    return render(request, "support/support.html")