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

        try:
            response = requests.post(
                f"{settings.BACKEND_URL}/register",
                json={"nombre": nombre, "email": email, "password": password},
                timeout=5
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
        except requests.exceptions.Timeout:
            messages.error(request, "El backend de FastAPI tardó demasiado en responder. Inténtalo de nuevo.")
            return redirect('register')
        except requests.exceptions.RequestException as e:
            messages.error(request, f"No se pudo conectar con el backend: {e}")
            return redirect('register')

    return render(request, 'register.html')

# Login de usuarios
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            response = requests.post(
                f"{settings.BACKEND_URL}/login",
                json={"email": email, "password": password},
                timeout=5
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    data = {}

                token = data.get("token") if data else None
                request.session["token"] = token

                user = authenticate(request, username=email, password=password)
                if user is None:
                    user = User.objects.filter(username=email).first()
                    if user is None:
                        user = User.objects.create_user(username=email, email=email, password=password)

                login(request, user)
                return redirect("cargar_documentos")
            else:
                messages.error(request, "Correo o contraseña incorrectos.")
        except requests.exceptions.Timeout:
            messages.error(request, "El servidor de autenticación no responde. Inténtalo más tarde.")
        except requests.exceptions.RequestException:
            messages.error(request, "Error de conexión con el servidor de inicio de sesión.")
            
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

# Documentos
@login_required
def cargar_documentos(request):
    aprendiz_info = None
    if request.method == "POST":
        tipo = request.POST.get("tipo_documento")
        programa = request.POST.get("programa")
        archivo = request.FILES.get("archivo")

        try:
            response = requests.post(
                f"{settings.BACKEND_URL}/ocr/upload/",
                files={"file": (archivo.name, archivo.read(), archivo.content_type)},
                data={"tipo_documento": tipo, "programa": programa},
                timeout=25
            )

            if response.status_code == 200:
                aprendiz_info = response.json()
                messages.success(request, "Documento procesado correctamente")
            else:
                messages.error(request, "Error al procesar el documento en el backend")

        except requests.exceptions.Timeout:
            messages.error(request, "El procesamiento del documento tomó demasiado tiempo. Verifica el backend.")
        except Exception as e:
            messages.error(request, f"Error al conectar con el backend: {e}")

    # Si no hay info, se muestran datos de prueba, pero sin notificación
    if not aprendiz_info:
        aprendiz_info = {
            "nombre": "Juan Pérez",
            "cedula": "123456789",
            "fecha_nacimiento": "1990-01-01",
            "programa": "Análisis de Datos"
        }

    return render(request, 'cargar_documentos.html', {'resultado': aprendiz_info})


# Historial de documentos
@login_required
def mis_documentos(request):
    documentos = []
    token = request.session.get("token")
    
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.get(f"{settings.BACKEND_URL}/documentos/", headers=headers, timeout=5)
        
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
