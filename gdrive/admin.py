from django.contrib import admin

# Register your models here.
from .models import driveModel,downloadHistory,Downloading

admin.site.register(driveModel)
admin.site.register(Downloading)
admin.site.register(downloadHistory)