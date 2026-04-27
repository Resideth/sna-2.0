from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=[("admin", "Administrador"), ("aprendiz", "Aprendiz")])

    def __str__(self):
        return f"{self.user.username} - {self.rol}"

class Documento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documentos")
    tipo_documento = models.CharField(max_length=100)
    archivo = models.FileField(upload_to="documentos/")

    def __str__(self):
        return f"{self.tipo_documento} de {self.usuario.username}"