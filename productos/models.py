# productos/models.py

from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

"""Se elimina el modelo Productos porque la app core maneja Producto.
Mantener este archivo sólo para Categoria."""
