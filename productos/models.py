# productos/models.py
from django.db import models

class Productos(models.Model):
    nombre_producto = models.CharField(max_length=100)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    # Referencias a otras apps
    id_marca = models.ForeignKey('marcas.Marca', on_delete=models.CASCADE)
    id_proveedor = models.ForeignKey('proveedores.Proveedores', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_producto
