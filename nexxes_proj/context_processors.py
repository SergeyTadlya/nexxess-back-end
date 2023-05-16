from services.models import ServiceCategory
from django.shortcuts import render


def category_for_menu(request):
    categories = ServiceCategory.objects.all()
    return {'categories': categories}