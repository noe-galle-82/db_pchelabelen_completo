from django.db import models
from core.models import EmpleadoProfile, Producto
from movimientos_caja.models import Caja 
from clientes.models import Clientes
from lotes.models import Lote
# Asumiendo que Productos, Clientes, y Estado_Venta están en sus Apps respectivas
# Necesitarías importar los modelos de sus Apps (ej: from productos.models import Producto)

# ==========================================================
# MODELO VENTA (Basado en tu DER)
# ==========================================================
class Venta(models.Model):
    # La Venta debe referenciar a la CAJA abierta (movimientos_caja)
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT) 
    # La Venta debe referenciar al EMPLEADO que la realiza (core)
    empleado = models.ForeignKey(EmpleadoProfile, on_delete=models.PROTECT, null=True, blank=True) 
    # Cliente (opcional: consumidor final)
    cliente = models.ForeignKey(Clientes, on_delete=models.PROTECT, null=True, blank=True)
    # Medio de pago (texto alineado con caja)
    medio_pago = models.CharField(max_length=20)
    # Número correlativo simple (opcional)
    numero = models.CharField(max_length=30, blank=True, null=True)
    # Notas opcionales
    notas = models.TextField(blank=True, null=True)
    # Idempotencia (para evitar duplicados por reintentos)
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
# MODELO DETALLE_VENTA (Basado en tu DER)
# ==========================================================
class DetalleVenta(models.Model):
    # id_venta (FN)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    # id_producto (FN)
    id_producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='ventas_detalles')
    # Lote utilizado (opcional si no se fuerza)
    id_lote = models.ForeignKey(Lote, on_delete=models.PROTECT, null=True, blank=True, related_name='ventas_detalles')
    
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    descuento_por_item = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name_plural = "Detalles de Venta"
        # primary_key conjunta si la necesitas (id_venta, id_producto)

    def __str__(self):
        return f"Detalle de Venta {self.id_venta.pk}"
