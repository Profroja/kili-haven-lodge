"""
URL configuration for kili project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import RedirectView
import os

def home_view(request):
    """Serve React frontend homepage"""
    # Path to your React build index.html in killhaven/dist
    react_build_path = os.path.join(settings.BASE_DIR.parent, 'killhaven', 'dist', 'index.html')
    
    try:
        with open(react_build_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        # Fallback if React build files are not found
        return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Kili - React Frontend</title>
        </head>
        <body>
            <h1>Welcome to Kili!</h1>
            <p>Please build your React app in the 'killhaven' folder.</p>
            <p>Run: <code>npm run build</code> in the killhaven directory</p>
            <p>API Endpoint: <a href="/api/home/">/api/home/</a></p>
        </body>
        </html>
        """, content_type='text/html')

urlpatterns = [
    path('', home_view, name='home'),  # Serve React frontend
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # API routes
    path('auth/', include('auths.urls')),  # Authentication routes
    path('manager/', include('kilimanager.urls')),  # Manager routes
    path('staff/', include('kilistaff.urls')),  # Staff routes
    
    # Favicon and icon URLs
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('favicon-16x16.png', RedirectView.as_view(url='/static/favicon-16x16.png', permanent=True)),
    path('favicon-32x32.png', RedirectView.as_view(url='/static/favicon-32x32.png', permanent=True)),
    path('android-chrome-192x192.png', RedirectView.as_view(url='/static/android-chrome-192x192.png', permanent=True)),
    path('android-chrome-512x512.png', RedirectView.as_view(url='/static/android-chrome-512x512.png', permanent=True)),
    path('apple-touch-icon.png', RedirectView.as_view(url='/static/apple-touch-icon.png', permanent=True)),
    path('site.webmanifest', RedirectView.as_view(url='/static/site.webmanifest', permanent=True)),
    path('robots.txt', RedirectView.as_view(url='/static/robots.txt', permanent=True)),
]

# Serve static files during development
if settings.DEBUG:
    # Serve static files from the static directory
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serve static files from STATICFILES_DIRS (your React build files)
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static('/static/', document_root=static_dir)
    # Serve assets folder specifically from killhaven/dist
    urlpatterns += static('/assets/', document_root=os.path.join(settings.BASE_DIR.parent, 'killhaven', 'dist', 'assets'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
