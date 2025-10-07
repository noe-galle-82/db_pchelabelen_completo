from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import Producto
from proveedores.models import Proveedores

class Lote(models.Model):
    producto = models.ForeignKey(Producto, related_name='lotes', on_delete=models.CASCADE)
    numero_lote = models.CharField(max_length=50, blank=True, null=True)
    cantidad_inicial = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    DESCUENTO_CHOICES = (
        ('porc', '%'),
        ('valor', '$'),
    )
    descuento_tipo = models.CharField(max_length=10, choices=DESCUENTO_CHOICES, blank=True, null=True)
    descuento_valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_compra = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    proveedor = models.ForeignKey(Proveedores, on_delete=models.PROTECT, null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'

    def __str__(self):
        return f"Lote {self.numero_lote or '-'} de {self.producto.nombre}"

    def costo_unitario_final(self):
        if self.costo_unitario is None:
            return None
        if self.descuento_tipo == 'porc' and self.descuento_valor:
            return float(self.costo_unitario) * (1 - (float(self.descuento_valor) / 100))
        if self.descuento_tipo == 'valor' and self.descuento_valor:
            if self.cantidad_inicial > 0:
                return float(self.costo_unitario) - (float(self.descuento_valor) / self.cantidad_inicial)
        return float(self.costo_unitario)

def _recalcular_stock_producto(producto):
    total = producto.lotes.aggregate(models.Sum('cantidad_disponible'))['cantidad_disponible__sum'] or 0
    if producto.cantidad != total:
        producto.cantidad = total
        producto.save(update_fields=['cantidad'])

@receiver(post_save, sender=Lote)
def actualizar_stock_post_save(sender, instance, **kwargs):
    _recalcular_stock_producto(instance.producto)

@receiver(post_delete, sender=Lote)
def actualizar_stock_post_delete(sender, instance, **kwargs):
    _recalcular_stock_producto(instance.producto)