from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import User
import threading
import requests
from .utils import resume_download
# Create your models here.
class driveModel(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="driveModel")
    json = models.TextField()

class Downloading(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    url = models.TextField()
    filename = models.CharField(blank=True, max_length=1000)
    progress = models.CharField(max_length=100)
    status = models.CharField(max_length=100,blank=True)
    downloaded_thread = models.TextField(blank=True)
    location = models.TextField(blank=True)
    size = models.TextField(blank=True)
    def resume(self):
        thread = threading.Thread(target=resume_download, args=(self,))
        thread.daemon = True
        thread.start()
class downloadHistory(models.Model):
    file = models.ForeignKey(Downloading,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)