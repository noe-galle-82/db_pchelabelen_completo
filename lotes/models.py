
from django.db import models
from productos.models import Productos

class Lotes(models.Model):

    
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    codigo_lote = models.CharField(max_length=50, unique=True) # Sugerencia: El código de lote debe ser único.
    precio_costo_unitario = models.DecimalField(max_digits=10, decimal_places=2) 
    cantidad_ingresada = models.IntegerField()
    stock = models.IntegerField()

    

    def __str__(self):
       
        return f"Lote {self.codigo_lote} de {self.id_producto.nombre_producto}"

    class Meta:
        # Asegura que el nombre de la tabla sea 'Lotes' si lo necesitas así
        db_table = 'Lotes'