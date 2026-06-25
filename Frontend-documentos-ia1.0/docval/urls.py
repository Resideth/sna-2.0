# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("api/register/", views.register_user, name="register"),
    path("api/login/", views.login_user, name="login"),
    path("api/logout/", views.logout_user, name="logout"),
]
