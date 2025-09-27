from django.db import models
from productos.models import Productos

class Lotes(models.Model):
    # La clave primaria 'id_lote' se crea automáticamente.
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    codigo_lote = models.CharField(max_length=50)
    cantidad_ingresada = models.IntegerField()
    stock = models.IntegerField()

    def __str__(self):
        return f"Lotes {self.codigo_lotes} de {self.id_producto.nombre_producto}"
