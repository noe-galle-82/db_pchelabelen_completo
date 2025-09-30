# models.py (en la app detalles_venta)
from django.db import models
from ventas.models import Venta 
from productos.models import Productos
from lotes.models import Lotes

class DetalleVenta(models.Model):
    
    id_detalle_venta = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles_venta')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    
    # Campo crucial en estado final: Obligatorio
    id_lote = models.ForeignKey(
        Lotes, 
        on_delete=models.PROTECT, 
        related_name='detalles_venta_lotes',
        null=False,    
        blank=False    
    )
    
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        # La línea estaba incompleta, ahora está cerrada correctamente
        return f"Venta {self.id_venta_id} - {self.cantidad}u. de {self.id_producto.nombre_producto} (Lote: {self.id_lote_id})"
    
    class Meta:
        db_table = 'detalle_venta'