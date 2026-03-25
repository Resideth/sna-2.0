from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Rutas de la aplicación principal "home"
    path('', include('home.urls')),  # conecta todas las rutas definidas en home/urls.py
]