from django.db import models
from django.contrib.auth.models import User

class Clientes(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    teléfono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    dni = models.CharField(max_length=10, blank=True, null=True, unique=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    CONDICION_IVA = (
        ("CF", "Consumidor Final"),
        ("RI", "Responsable Inscripto"),
        ("MT", "Monotributo"),
        ("EX", "Exento"),
        ("NR", "No Responsable"),
    )
    condicion_iva = models.CharField(max_length=2, choices=CONDICION_IVA, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre_completo

