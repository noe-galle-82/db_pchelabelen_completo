from django.db import models

class Proveedores(models.Model):
    nombre_proveedor = models.CharField(max_length=100)
    localidad = models.CharField(max_length=50)
    teléfono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre_proveedor
