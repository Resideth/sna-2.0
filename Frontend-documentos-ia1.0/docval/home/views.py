from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, Documento

import requests
from django.conf import settings

# Página principal (puedes dejarla si la usas en otra parte)
def home_view(request):
    return render(request, 'home.html')

# Registro de usuarios
def register_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, "El correo ya está registrado")
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nombre
            )
            user.save()

            PerfilUsuario.objects.create(user=user)

            messages.success(request, "Usuario registrado correctamente")
            return redirect('login')

    return render(request, 'login.html')

# Login de usuarios
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            # 🔹 Aquí cambiamos la redirección para que vaya a cargar_documentos
            return redirect("cargar_documentos")
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
    return render(request, "login.html")

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('login')

# Dashboards (puedes eliminarlos si ya no usas roles)
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def aprendiz_dashboard(request):
    return render(request, 'cargar_documentos.html')

# Documentos (única vista)
@login_required
def cargar_documentos(request):
    aprendiz_info = None
    if request.method == "POST":
        tipo = request.POST.get("tipo_documento")
        archivo = request.FILES.get("archivo")

        if archivo:
            Documento.objects.create(usuario=request.user, tipo_documento=tipo, archivo=archivo)
            try: 
                response = requests.post(
                    f"{settings.BACKEND_URL}/ocr/upload/",
                    files={"file": archivo},
                )

                if response.status_code == 200:
                    resultado = response.json()
                    aprendiz_info = resultado
                    messages.success(request, "Documento procesado correctamente")
                else:
                    messages.error(request, "Error al procesar el documento en el backend")

            except Exception as e:
                messages.error(request, f"Error al procesar el documento en el backend: {e}")

    if not aprendiz_info:
        aprendiz_info = {
            "nombre": "Juan Pérez",
            "cedula": "123456789",
            "fecha_nacimiento": "1990-01-01",
            "programa": "Análisis de Datos"
        } 

    return render(request, 'cargar_documentos.html', {'resultado': aprendiz_info})

@login_required
def mis_documentos(request):
    documentos = Documento.objects.filter(usuario=request.user)
    return render(request, 'mis_documentos.html', {'documentos': documentos})

@login_required
def reportes_view(request):
    return render(request, 'reportes.html')
