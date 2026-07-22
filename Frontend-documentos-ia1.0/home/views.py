from django.shortcuts import render, redirect
from django.contrib.auth import logout  # Solo logout (no necesitamos login/authenticate)
from django.contrib import messages
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

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

         logger.info(f"🔍 Enviando registro: nombre={nombre}, email={email}, password={password}")
             
        try:
            response = requests.post(
                f"{settings.BACKEND_URL}/register",
                json={"nombre": nombre, "email": email, "password": password},
                timeout=5
            )

             logger.info(f"📩 Respuesta del backend: status={response.status_code}, body={response.text}")

            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                # Ahora el registro devuelve usuario_id, pero NO token
                # Si el registro no devuelve token, debemos hacer login después
                usuario_id = data.get("usuario_id")
                # Guardamos usuario_id en sesión
                request.session["usuario_id"] = usuario_id
                messages.success(request, "Usuario registrado correctamente")
                # Redirigir al login para que el usuario inicie sesión
                return redirect('cargar_documentos')
            
            else:                    
                error_msg = response.json().get("detail", response.text)
                messages.error(request, f"Error al registrar: {error_msg}")
                return redirect('register')

        except requests.exceptions.Timeout:
            messages.error(request, "El backend de FastAPI tardó demasiado en responder. Inténtalo de nuevo.")
            return redirect('register')
        except requests.exceptions.RequestException as e:
            messages.error(request, f"No se pudo conectar con el backend: {e}")
            return redirect('register')

    return render(request, 'login.html')

# Login de usuarios
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            response = requests.post(
                f"{settings.BACKEND_URL}/login",
                json={"email": email, "password": password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                usuario_id = data.get("usuario_id")
                request.session["token"] = token
                request.session["usuario_id"] = usuario_id
                
                 request.session["token"] = token
                request.session["usuario_id"] = usuario_id
                request.session["email"] = email
                
                messages.success(request, "Login exitoso")
                if email.strip().lower() == "admin@institucion.edu.co":
                    return redirect("admin_dashboard")
                else:
                    return redirect("cargar_documentos")

            else:
                messages.error(request, "Correo o contraseña incorrectos.")
                return redirect("login")
                
        except requests.exceptions.Timeout:
            messages.error(request, "El servidor de autenticación no responde. Inténtalo más tarde.")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error de conexión con el servidor: {e}")

    return render(request, "login.html")

# Logout
def logout_view(request):
    # Limpiar la sesión manualmente (no usamos logout de Django)
    request.session.flush()
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('login')

# ---- Decorador personalizado para verificar token ----
def token_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("token"):
            messages.error(request, "Debes iniciar sesión primero.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# Dashboards
@token_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@token_required
def aprendiz_dashboard(request):
    return render(request, 'cargar_documentos.html')

# Documentos
@token_required
def cargar_documentos(request):
    aprendiz_info = None
    if request.method == "POST":
        tipo_documento = request.POST.get("tipo_documento")
        programa = request.POST.get("programa")
        archivo = request.FILES.get("archivo")

        if archivo and tipo_documento and programa:
            token = request.session.get("token")
            # CORREGIR: "Authorization" (estaba "Autorization")
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            
            response = requests.post(
                f"{settings.BACKEND_URL}/ocr/upload/",
                files={"file": archivo},
                data={
                    "tipo_documento": tipo_documento, 
                    "programa": programa, 
                    "modelo": "hologramas",
                    "usuario_id": request.session.get("usuario_id")
                },
                headers=headers, 
                timeout=30
            )
            
            logging.warning("Respuesta backend: %s", response.text)
            if response.status_code == 200:
                aprendiz_info = response.json()
                messages.success(request, "Documento procesado correctamente")
            else:
                messages.error(request, f"Error al subir documento: {response.text}")

    return render(request, "cargar_documentos.html", {"aprendiz_info": aprendiz_info})

# Historial de documentos
@token_required
def mis_documentos(request):
    documentos = []
    token = request.session.get("token")
    
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.get(
            f"{settings.BACKEND_URL}/documentos/", 
            headers=headers, 
            timeout=5
        )
        
        if response.status_code == 200:
            documentos = response.json()
        else:
            messages.error(request, f"Error al obtener documentos: {response.text}")
    except requests.exceptions.Timeout:
        messages.error(request, "El servidor tardó demasiado en responder al solicitar documentos.")
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al obtener documentos: {e}")

    return render(request, 'mis_documentos.html', {'documentos': documentos})

@token_required
def reportes_view(request):
    return render(request, 'reportes.html')
