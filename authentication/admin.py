from django.contrib import admin
from .models import B24keys


@admin.register(B24keys)      # register in admin panel b24 keys
class B24keysAdmin(admin.ModelAdmin):
    list_display = ['id']

