from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from unfold.admin import ModelAdmin


class AutoModelAdmin(ModelAdmin):
    pass


for model in apps.get_app_config("accounts").get_models():
    try:
        admin.site.register(model, AutoModelAdmin)
    except AlreadyRegistered:
        continue
