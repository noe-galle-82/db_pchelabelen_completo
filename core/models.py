from django.db import models
from django.contrib.auth.models import User

# ==========================================================
# 1. PERFIL DE EMPLEADO (Sustituye a la tabla Usuarios para fines de negocio)
# ==========================================================
class EmpleadoProfile(models.Model):
    # Enlazamos al usuario de Django (tabla auth_user)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario del Sistema')
    # Campos que vienen de la tabla Usuarios y Tipo_usuario
    nombre_tipo_usuario = models.CharField(max_length=50, blank=True, verbose_name='Rol (Cajero/Repositor)') # Usado para referencia rápida
    
    # Nuevo campo para identificar al empleado en la empresa
    numero_empleado = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    # Campo de la tabla Usuarios que usaríamos del modelo de Django: email_usuario -> user.email
    # Campo de la tabla Usuarios que usaríamos del modelo de Django: password_hash -> user.password

    def __str__(self):
        return f"Empleado: {self.user.username} ({self.nombre_tipo_usuario})"