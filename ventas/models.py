from django.db import models
from core.models import EmpleadoProfile
from movimientos_caja.models import Caja 
# Asumiendo que Productos, Clientes, y Estado_Venta están en sus Apps respectivas
# Necesitarías importar los modelos de sus Apps (ej: from productos.models import Producto)

# ==========================================================
# MODELO VENTA (Basado en tu DER)
# ==========================================================
class Venta(models.Model):
    # La Venta debe referenciar a la CAJA abierta (movimientos_caja)
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT) 
    # La Venta debe referenciar al EMPLEADO que la realiza (core)
    empleado = models.ForeignKey(EmpleadoProfile, on_delete=models.PROTECT) 

    # Atributos de tu DER (adaptados)
    # id_cliente = models.ForeignKey(Clientes, on_delete=models.PROTECT) # Si tienes esta app
    # id_estado_venta = models.ForeignKey(EstadoVenta, on_delete=models.PROTECT) # Si tienes esta app
    
    fecha_venta = models.DateField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    
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
    # id_producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Si tienes esta app
    
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name_plural = "Detalles de Venta"
        # primary_key conjunta si la necesitas (id_venta, id_producto)

    def __str__(self):
        return f"Detalle de Venta {self.id_venta.pk}"
