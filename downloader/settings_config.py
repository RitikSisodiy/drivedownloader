import os
ENV = os.getenv("ENV")
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
configuration = {
    "DEV":{
        "DEBUG" : True,
        "DATABASES" : {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    },
    "PROD":{
        "DEBUG" : False,
        "DATABASES" : {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'downloaddrive',
                'USER': 'admin',
                'PASSWORD': 'ujmHAyQOtsc2ntd7uy1kprqovy19FrJO',
                'HOST': 'dpg-clheqq6bbf9s73b0tang-a',  # Set to your PostgreSQL server's host if not on the local machine
                'PORT': '5432',      # Default PostgreSQL port
            }
        }
    }
}

configuration = configuration[ENV]
