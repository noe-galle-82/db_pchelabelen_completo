from django.db import models
from django.contrib.auth.models import User

# ==========================================================
# 1. PERFIL DE EMPLEADO (Extiende el modelo de Usuario de Django)
# ==========================================================
class EmpleadoProfile(models.Model):
    # Enlace UNO A UNO al usuario de autenticación de Django (tabla auth_user)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario del Sistema')
    
    # ---------------------------------------------
    # INFORMACIÓN PERSONAL BÁSICA REQUERIDA
    # ---------------------------------------------
    nombre = models.CharField(max_length=100, verbose_name='Nombre(s)', null=False, default='pendiente')
    apellidos = models.CharField(max_length=150, verbose_name='Apellidos', default='pendiente', null=False)
    
    # 🌟 CAMBIO CRÍTICO: Se elimina null=True y blank=True para hacerlo OBLIGATORIO
    # (El DNI debe ser rellenado antes de aplicar la próxima migración).
    dni = models.CharField(max_length=15, unique=True, verbose_name='DNI/Cédula') 
    
    # ---------------------------------------------
    # DATOS DE NACIMIENTO Y NACIONALIDAD
    # ---------------------------------------------
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    lugar_nacimiento = models.CharField(max_length=100, null=True, blank=True, verbose_name='Lugar de Nacimiento')
    nacionalidad = models.CharField(max_length=50, null=True, blank=True, verbose_name='Nacionalidad')
    
    # ---------------------------------------------
    # DATOS DE CONTACTO Y UBICACIÓN
    # ---------------------------------------------
    telefono = models.CharField(max_length=20, verbose_name='Teléfono/Celular', null=False, default='pendiente')
    # El email del sistema es user.email, este es un email personal opcional
    email_personal = models.EmailField(max_length=100, verbose_name='Email Personal (Opcional)', null=False, default='pendiente')
    direccion = models.CharField(max_length=255, null=True, blank=True, verbose_name='Dirección de Domicilio')
    
    # ---------------------------------------------
    # CONTACTO DE EMERGENCIA
    # ---------------------------------------------
    contacto_emergencia = models.CharField(max_length=100, null=True, blank=True, verbose_name='Contacto de Emergencia')
    
    # ---------------------------------------------
    # CAMPOS DE NEGOCIO Y ROL (Los que ya tenías)
    # ---------------------------------------------
    nombre_tipo_usuario = models.CharField(max_length=50, blank=True, verbose_name='Rol (Cajero/Repositor)') 
    numero_empleado = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    class Meta:
        db_table = 'core_empleadoprofile' 
        verbose_name = 'Perfil de Empleado'
        verbose_name_plural = 'Perfiles de Empleados'

    def __str__(self):
        return f"{self.nombre} {self.apellidos} | Rol: {self.nombre_tipo_usuario}"