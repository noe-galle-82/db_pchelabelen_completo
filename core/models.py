from django.db import models
from django.contrib.auth.models import User

# ============================================================================== 
# 1. Modelo Base (Abstracto)
# ==============================================================================

class BaseModel(models.Model):
    # Campo de fecha y hora para registro de creación
    created_at = models.DateTimeField(auto_now_add=True)
    # Campo de fecha y hora para registro de la última modificación
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
# ============================================================================== 
# 2. Modelo Empleados
# ==============================================================================

class Empleados(BaseModel):
    # Relación uno a uno con el usuario de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.dni})"
        
# ============================================================================== 
# 3. Modelo EmpleadoProfile
# ==============================================================================

class EmpleadoProfile(BaseModel):
    # Se relaciona con el modelo Empleados
    empleado = models.OneToOneField(Empleados, on_delete=models.CASCADE)
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.empleado.nombre} {self.empleado.apellido}"

