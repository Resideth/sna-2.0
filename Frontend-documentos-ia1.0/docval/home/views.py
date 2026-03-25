from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, Documento

import requests
from django.conf import settings

# Página principal
def home_view(request):
    return render(request, 'home.html')

# Registro de usuarios
def register_view(request):
    if request.method == "POST":
        nombre = request.POST['username'] 
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, "El correo ya está registrado")
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = nombre
            user.save()

            # asignar rol automático
            rol = "admin" if email.endswith("@institucion.edu.co") else "aprendiz"
            PerfilUsuario.objects.create(user=user, rol=rol)

            messages.success(request, "Usuario registrado correctamente")
            return redirect('login')

    return render(request, 'login.html')

# Login de usuarios
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if hasattr(user, "perfil"):
                if user.perfil.rol == "admin":
                    return redirect('admin_dashboard')
                elif user.perfil.rol == "aprendiz":
                    return redirect('aprendiz_dashboard')
            else:
                messages.error(request, "El usuario no tiene perfil asociado")
        else:
            messages.error(request, "Credenciales inválidas")
    return render(request, 'login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboards
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def aprendiz_dashboard(request):
    return render(request, 'cargar_documentos.html')

# Documentos (única vista)
@login_required
def cargar_documentos(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo_documento")
        archivo = request.FILES.get("archivo")

        if archivo:
            Documento.objects.create(usuario=request.user, tipo_documento=tipo, archivo=archivo)
            response = requests.post(
                f"{settings.BACKEND_URL}/ocr/upload/",
                files={"file": archivo},
            )
            if response.status_code == 200:
                resultado = response.json()
                messages.success(request, f"Documento procesado: {resultado}")
            else:
                messages.error(request, "Error al procesar el documento en el backend")

            return redirect('mis_documentos')

    # Siempre renderiza la misma plantilla con criterios incluidos
    return render(request, 'cargar_documentos.html')

@login_required
def mis_documentos(request):
    documentos = Documento.objects.filter(usuario=request.user)
    return render(request, 'mis_documentos.html', {'documentos': documentos})

@login_required
def reportes_view(request):
    return render(request, 'reportes.html')