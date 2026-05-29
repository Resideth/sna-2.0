from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings

# Página principal
def home_view(request):
    return render(request, 'home.html')

# Registro de usuarios
def register_view(request):
    if request.method == "POST":
        nombre = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('register')

        # Enviar datos al backend FastAPI
        response = requests.post(
            f"{settings.BACKEND_URL}/register",
            json={"nombre": nombre, "email": email, "password": password}
        )

        if response.status_code == 200:
            messages.success(request, "Usuario registrado correctamente")
            return redirect('login')
        else:
            try: 
                error_data = response.json()
                error_msg = error_data.get("detail", response.text)
            except Exception:
                error_msg = response.text
            
            messages.error(request, f"Error al registrar: {error_msg}")
            return redirect('register')

    return render(request, 'login.html')

# Login de usuarios
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Autenticación contra FastAPI
        response = requests.post(
            f"{settings.BACKEND_URL}/login",
            json={"email": email, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            request.session["token"] = data.get("token")

            # Autenticación también en Django para mantener la sesión web
            user = authenticate(request, username=email, password=password)
            if user is None:
                user = User.objects.filter(username=email).first()
                if user is None:
                    user = User.objects.create_user(username=email, email=email, password=password)

            login(request, user)
            return redirect("cargar_documentos")
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
    return render(request, "login.html")

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('login')

# Dashboards
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def aprendiz_dashboard(request):
    return render(request, 'cargar_documentos.html')

# Documentos (Corregido: Sin guardar en base de datos local)
@login_required
def cargar_documentos(request):
    aprendiz_info = None
    if request.method == "POST":
        tipo = request.POST.get("tipo_documento")
        archivo = request.FILES.get("archivo")

        if archivo:
            try: 
                # Enviamos el archivo directamente a FastAPI junto con el tipo de documento
                response = requests.post(
                    f"{settings.BACKEND_URL}/ocr/upload/",
                    files={"file": (archivo.name, archivo.read(), archivo.content_type)},
                    data={"tipo_documento": tipo} # Si tu backend acepta el tipo, lo enviamos aquí
                )

                if response.status_code == 200:
                    aprendiz_info = response.json()
                    messages.success(request, "Documento procesado correctamente")
                else:
                    messages.error(request, "Error al procesar el documento en el backend")

            except Exception as e:
                messages.error(request, f"Error al conectar con el backend: {e}")

    if not aprendiz_info:
        # Datos de prueba por defecto si no se ha subido nada o falló
        aprendiz_info = {
            "nombre": "Juan Pérez",
            "cedula": "123456789",
            "fecha_nacimiento": "1990-01-01",
            "programa": "Análisis de Datos"
        } 

    return render(request, 'cargar_documentos.html', {'resultado': aprendiz_info})

# Historial de documentos (Corregido: Consulta a FastAPI)
@login_required
def mis_documentos(request):
    documentos = []
    token = request.session.get("token")
    
    try:
        # Le pedimos la lista de documentos al backend usando el token del usuario
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.get(f"{settings.BACKEND_URL}/documentos/", headers=headers)
        
        if response.status_code == 200:
            documentos = response.json()
        else:
            messages.warning(request, "No se pudo obtener el historial de documentos.")
    except Exception:
        messages.error(request, "Error de conexión al obtener el historial.")

    return render(request, 'mis_documentos.html', {'documentos': documentos})

@login_required
def reportes_view(request):
    return render(request, 'reportes.html')
