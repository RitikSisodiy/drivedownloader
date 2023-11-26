from django.urls import path
from .import views 

urlpatterns = [
    # Other URLs
    path('auth/google_drive/', views.authenticate, name='google_drive_auth'),
    path('auth/google_drive/callback/', views.auth_callback, name='google_drive_callback'),
    path('', views.success_page, name='success_page'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('download/', views.startDownloading, name='download'),
    path('delete/', views.deleteDownloading, name='delete'),
    # Add other URLs as needed
]

