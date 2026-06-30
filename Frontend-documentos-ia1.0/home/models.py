from django.db import models
from django.contrib.auth.models import User

# Perfil de usuario con rol (admin o aprendiz)
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(
        max_length=20,
        choices=[("admin", "Admin"), ("aprendiz", "Aprendiz")],
        default="aprendiz"
    )

    def __str__(self):
        return f"{self.user.username} - {self.rol}"


# Documentos subidos por los usuarios
class Documento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to="documentos/")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ("aprobado", "Aprobado"),
            ("rechazado", "Rechazado"),
            ("pendiente", "Pendiente")
        ],
        default="pendiente"
    )

    def __str__(self):
        return f"{self.nombre} ({self.estado})"
