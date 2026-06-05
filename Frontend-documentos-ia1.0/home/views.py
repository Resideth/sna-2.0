from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests
import logging
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
                # 🔹 Crear usuario en Django si no existe
                user = User.objects.filter(username=email).first()
                if user is None:
                    user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)

                login(request, user)

                # 🔹 Redirigir según el correo
                if email.strip().lower() == "admin@institucion.edu.co":
                    return redirect("admin_dashboard")
                else:
                    return redirect("cargar_documentos")

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

    return render(request, "login.html")  # 🔹 ya no necesitas register.html



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
        archivo = request.FILES.get("archivo")
        if archivo:
            response = requests.post(
                f"{settings.BACKEND_URL}/ocr/upload/",
                files={"file": archivo},
            )
            logging.warning("Respuesta backend: %s", response.text)  # 🔹 imprime el JSON real
            if response.status_code == 200:
                aprendiz_info = response.json()
    return render(request, "cargar_documentos.html", {"aprendiz_info": aprendiz_info})
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
    except requests.exceptions.Timeout:
        messages.error(request, "El servidor tardó demasiado en responder al solicitar documentos.")
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al obtener documentos: {e}")

    return render(request, 'mis_documentos.html', {'documentos': documentos})

@login_required
def reportes_view(request):
    return render(request, 'reportes.html')
