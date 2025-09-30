from django.db import models

class Productos(models.Model):
    """
    Modelo para representar un producto en el inventario.
    El nombre de la clase es 'Productos' para coincidir con la referencia 
    que usamos en 'detalles_venta.DetalleVenta'.
    """
    nombre = models.CharField(
        max_length=255, 
        verbose_name="Nombre del Producto",
        unique=True
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    precio_venta = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio de Venta"
    )
    stock_actual = models.IntegerField(
        default=0,
        verbose_name="Stock Actual"
    )
    
    # Podrías agregar una clave foránea a Categoría si existe.

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
