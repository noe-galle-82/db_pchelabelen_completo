from django.db import models
from django.contrib.auth.models import User

class Clientes(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    teléfono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.nombre_completo

