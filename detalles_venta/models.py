from django.db import models

class DetalleVenta(models.Model):
    """
    Representa una línea de producto dentro de una venta.
    """
    # CLAVE CORREGIDA: Referencia al modelo Productos (en plural)
    venta = models.ForeignKey('ventas.Venta', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Productos', on_delete=models.CASCADE)
    
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad"
    )
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio Unitario"
    )

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Ventas"
        # Aseguramos que un producto solo se pueda añadir una vez por venta
        unique_together = ('venta', 'producto') 
        
    def __str__(self):
        # Usamos try/except porque durante la migración puede que venta o producto no estén cargados aún
        try:
            return f"Detalle Venta {self.venta.id} - {self.producto.nombre}"
        except:
            return f"Detalle Venta (Pendiente de carga)"
