from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Authenticate the client.
gauth = GoogleAuth()
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)