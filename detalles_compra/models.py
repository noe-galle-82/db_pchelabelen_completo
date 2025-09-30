# detalles_compra/models.py (Ubicación asumida)

from django.db import models

# Importar modelos de otras aplicaciones
# CRÍTICO: Debes importar los modelos desde sus apps CORRECTAS
from compras.models import Compras 
from productos.models import Productos
from lotes.models import Lotes 

# ----------------------------------------------------------------------
# MODELO DE DETALLE: DetalleCompra
# ----------------------------------------------------------------------

class DetalleCompra(models.Model):
    """
    Modelo para registrar los detalles (productos, cantidad, precio) de una compra específica.
    """
    id_detalle_compra = models.AutoField(primary_key=True)
    
    # 1. Relación con Compras
    # El related_name es correcto para evitar colisiones.
    id_compra = models.ForeignKey(
        Compras, 
        on_delete=models.CASCADE, 
        related_name='detalles_de_compra_app', 
        verbose_name="Compra"
    ) 

    # 2. Relación con Productos
    id_producto = models.ForeignKey(
        Productos, 
        on_delete=models.PROTECT, 
        related_name='detalles_de_producto_app',
        verbose_name="Producto"
    )
    
    # 3. Relación con Lotes
    # **IMPORTANTE:** En tu views.py, este campo se asigna DESPUÉS de guardar el detalle.
    # Por lo tanto, debe ser NULL=TRUE y BLANK=TRUE al crearse (solo se llena después).
    id_lote = models.ForeignKey(
        Lotes, 
        on_delete=models.PROTECT, 
        related_name='detalles_compra_lotes', 
        null=True,     # <--- ¡CORREGIDO! Debe ser null=True para la lógica de views.py
        blank=True,    # <--- ¡CORREGIDO! Debe ser blank=True para la lógica de views.py
        verbose_name="Lote Asociado"
    )
    
    cantidad = models.IntegerField(verbose_name="Cantidad")
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    def __str__(self):
        # Corregí el acceso al nombre del producto
        return f"Compra {self.id_compra_id} - {self.cantidad}u. de {self.id_producto.nombre_producto}"

    class Meta:
        db_table = 'detalle_compra'
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compras"