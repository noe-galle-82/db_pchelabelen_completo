from django.db import models
from django.contrib.auth.models import User
from proveedores.models import Proveedores # Asumo que el modelo se llama Proveedores
from tipo_pago.models import TipoPago # Asumo que el modelo se llama TipoPago

# ----------------------------------------------------------------------
# 1. MODELO PRINCIPAL: Compras (La Transacción)
# ----------------------------------------------------------------------

class Compras(models.Model):
    # Clave primaria por defecto: id (Django la crea automáticamente)

    # Relación con el usuario que realiza la compra
    id_empleado = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Empleado"
    )

    # Relación con el proveedor
    id_proveedor = models.ForeignKey(
        Proveedores, 
        on_delete=models.PROTECT, 
        verbose_name="Proveedor"
    )

    # Relación con el tipo de pago (Efectivo, Tarjeta, etc.)
    id_tipo_pago = models.ForeignKey(
        TipoPago, 
        on_delete=models.PROTECT, 
        verbose_name="Tipo de Pago"
    )

    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total de la Compra", default=0) # Añadimos default
    
    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        # Usamos 'fecha' en lugar de '-fecha_registro'
        ordering = ['-fecha'] 
        
    def __str__(self):
        # Usamos self.pk o self.id (son el mismo)
        return f"Compra N° {self.pk} - Total: ${self.total}"

# ----------------------------------------------------------------------
#
# ----------------------------------------------------------------------
 
