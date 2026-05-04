from django.urls import path
from .views import (
    home_view, register_view, login_view, logout_view,
    admin_dashboard, aprendiz_dashboard,
    cargar_documentos, mis_documentos,
    reportes_view   # <-- mantenemos la vista de reportes
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('aprendiz_dashboard/', aprendiz_dashboard, name='aprendiz_dashboard'),
    path('cargar_documentos/', cargar_documentos, name='cargar_documentos'),
    path('mis_documentos/', mis_documentos, name='mis_documentos'),
    path('reportes/', reportes_view, name='reportes'),  # ruta para reportes
]