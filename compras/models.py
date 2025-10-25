from lotes.models import Lote
from django.db import models

class Compras(models.Model):
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateField(auto_now_add=True)
    # Referencias a otras apps
    id_proveedor = models.ForeignKey('proveedores.Proveedores', on_delete=models.CASCADE)
    id_usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'Compra #{self.id}'


class DetalleCompra(models.Model):
    id_compra = models.ForeignKey(Compras, on_delete=models.CASCADE, related_name='detalles')
    id_lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name='compras_detalles')
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    descuento_por_item = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name_plural = "Detalles de Compra"

    def __str__(self):
        return f"Detalle de Compra {self.id_compra.pk}"
