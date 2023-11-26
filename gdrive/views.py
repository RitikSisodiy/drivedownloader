from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.conf import settings
import threading
from .utils import download_file
from .models import driveModel,Downloading
def get_drive_service(credentials):
    return build('drive', 'v2', credentials=credentials)
@login_required(login_url = "/login")
def authenticate(request):
    current_host =  ((request.is_secure() and "https://") or "http://") + request.get_host()
    # Use your own CLIENT_ID and CLIENT_SECRET obtained from the Google Cloud Console
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    flow = InstalledAppFlow.from_client_config(
        settings.GDRIVE_CLIENT_SECRET_CONFIG,  # Path to your downloaded client_secrets.json
        scopes=SCOPES,redirect_uri=f'{current_host}/auth/google_drive/callback' 
    )

    auth_url, _ = flow.authorization_url(prompt='consent')

    return redirect(auth_url)

@login_required(login_url = "/login")
def auth_callback(request):
    current_host =  ((request.is_secure() and "https://") or "http://") + request.get_host()
    flow = InstalledAppFlow.from_client_config(
        settings.GDRIVE_CLIENT_SECRET_CONFIG,   # Path to your downloaded client_secrets.json
        scopes=['https://www.googleapis.com/auth/drive.file'],
        
        redirect_uri=f'{current_host}/auth/google_drive/callback'
    )

    flow.fetch_token(authorization_response=request.build_absolute_uri())
    driveModel(user=request.user,json=flow.credentials.to_json()).save()
    return redirect('success_page')  # Redirect to a success page
@login_required(login_url = "/login")
def success_page(request):
    # Load credentials from the session
    credentials_json = driveModel.objects.filter(user=request.user.id).first()
    if not credentials_json:
        return redirect("google_drive_auth")
    # credentials_json = credentials_json.json
    # credentials = Credentials.from_authorized_user_info(json.loads(credentials_json))

    # # Use the credentials to interact with the user's Google Drive
    # drive_service = get_drive_service(credentials)

    # # Perform actions on the user's Google Drive (e.g., list files)
    # files = drive_service.files().list().execute()
    files = Downloading.objects.filter(user=request.user.id).values()
    print(files)
    return render(request, 'success_page.html', {'files': files})
 
def startDownloading(request):
    if request.method =="POST":
        url = request.POST["url"]
        Downloadingob = Downloading(url=url,user=request.user,progress="0")
        Downloadingob.save()
        thread=threading.Thread(target=download_file, args=(url,8,"",Downloadingob))
        thread.start()
        return redirect("success_page")
    pass
def deleteDownloading(request):
    try:
        Downloading.objects.get(pk=request.GET["id"]).delete()
    except:
        pass
    finally:
        return redirect("success_page")
from django.contrib.auth.forms import AuthenticationForm ,UserCreationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

def custom_login(request):
    print(request.user)
    if request.user.is_authenticated:
        return redirect("success_page")
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('success_page')  # Change 'home' to the name of your home view
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')  # Change 'home' to the name of your home view
def signup(request):
    if request.user.is_authenticated:
        return redirect("success_page")
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('success_page')  # Change 'home' to the name of your home view
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})