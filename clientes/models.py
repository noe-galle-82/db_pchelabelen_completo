from django.db import models
from django.contrib.auth.models import User


class Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
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
        return f"{self.nombre} {self.apellido}"

