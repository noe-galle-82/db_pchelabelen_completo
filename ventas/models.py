from django.db import models
from core.models import EmpleadoProfile, Producto
from movimientos_caja.models import Caja 
from clientes.models import Clientes
from lotes.models import Lote


# ==========================================================
# MODELO VENTA
# ==========================================================
class Venta(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT)
    empleado = models.ForeignKey(EmpleadoProfile, on_delete=models.PROTECT, null=True, blank=True)
    cliente = models.ForeignKey('clientes.Clientes', on_delete=models.PROTECT, null=True, blank=True)
    medio_pago = models.CharField(max_length=20)
    numero = models.CharField(max_length=30, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    idempotency_key = models.CharField(max_length=100, blank=True, null=True, unique=True)

    fecha_venta = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name_plural = "Ventas"
        permissions = [
            ("can_view_sale_details", "Puede ver los detalles de cualquier venta"),
        ]

    def __str__(self):
        return f"Venta N°{self.pk} - Total: {self.monto_total}"


# ==========================================================
# MODELO DETALLE_VENTA
# ==========================================================
class DetalleVenta(models.Model):
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    id_producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='ventas_detalles')
    id_lote = models.ForeignKey(Lote, on_delete=models.PROTECT, null=True, blank=True, related_name='ventas_detalles')

    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    # 👇 CAMBIO CLAVE: default=0, así nunca rompe si no se envía desde React
    descuento_por_item = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default=0
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"Detalle de Venta {self.id_venta.pk}"
