from django.db import models
from compras.models import Compras
from productos.models import Productos
from lotes.models import Lotes

class DetalleCompra(models.Model):
    id_detalle_compra = models.AutoField(primary_key=True)
    id_compra = models.ForeignKey(Compras, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    
    # Campo crucial en estado final: Obligatorio
    id_lote = models.ForeignKey(
        Lotes, 
        on_delete=models.PROTECT, 
        related_name='detalles_compra_lotes', 
        null=False,   # <--- Correcto: Restricción final
        blank=False   # <--- Correcto: Restricción final
    )
    
    cantidad = models.IntegerField() 
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Compra {self.id_compra_id} - {self.cantidad}u. de {self.id_producto.nombre_producto} (Lote: {self.id_lote_id})"

    class Meta:
        db_table = 'detalle_compra'