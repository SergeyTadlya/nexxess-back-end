from django.contrib import admin
from .models import B24keys


@admin.register(B24keys)
class B24keysAdmin(admin.ModelAdmin):
    list_display = ['id']

