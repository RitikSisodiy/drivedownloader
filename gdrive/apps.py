from django.apps import AppConfig
import threading,time
import requests
def callService():
    url = "https://drivedownloader.onrender.com/login/"
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    requests.get(url,headers=headers)
    time.sleep(20)
    callService()

class GdriveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gdrive'
    def ready(self):
        thread = threading.Thread(target=callService, args=())
        thread.start()