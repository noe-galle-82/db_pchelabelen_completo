from django.db import models
from core.models import EmpleadoProfile 
from tipo_movimientos.models import TipoMovimiento # Importamos el modelo
from tipo_pago.models import TipoPago # Importamos el modelo

# ==========================================================
# 1. MODELO CAJA (Control de Apertura y Cierre - Relación con Roles)
# ==========================================================
class Caja(models.Model):
    empleado_apertura = models.ForeignKey(
        EmpleadoProfile, 
        related_name='cajas_abiertas', 
        on_delete=models.PROTECT,
        verbose_name='Empleado Apertura'
    )
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    
    empleado_cierre = models.ForeignKey(
        EmpleadoProfile, 
        related_name='cajas_cerradas', 
        null=True, blank=True, 
        on_delete=models.PROTECT,
        verbose_name='Empleado Cierre'
    )
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    ESTADOS = (
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ABIERTA')
    
    class Meta:
        verbose_name_plural = "Cajas"
        permissions = [
            ("can_open_cash_register", "Puede abrir y cerrar la caja"),
        ]

    def __str__(self):
        return f"Caja N°{self.pk} - {self.estado}"


# ==========================================================
# 2. MODELO MOVIMIENTOS_DE_CAJA (Transacciones - Basado en tu DER)
# ==========================================================
class MovimientoDeCaja(models.Model):
    # Referencia obligatoria a la CAJA que está abierta
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name='movimientos')
    
    # Atributos de tu DER
    fecha_movimiento = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    # REFERENCIAS CORREGIDAS: 
    # id_usuario ahora es empleado (usando EmpleadoProfile)
    empleado = models.ForeignKey(
        EmpleadoProfile, 
        on_delete=models.PROTECT, 
        verbose_name='Empleado'
    )
    
    # Referencias a otras apps (usando el nombre de modelo correcto)
    id_tipo_movimiento = models.ForeignKey(
        TipoMovimiento,
        on_delete=models.PROTECT, 
        verbose_name='Tipo de Movimiento'
    )
    id_tipo_pago = models.ForeignKey(
        TipoPago, 
        on_delete=models.PROTECT,
        verbose_name='Tipo de Pago'
    )
    
    class Meta:
        verbose_name_plural = "Movimientos de Caja"

    def __str__(self):
        return f'Mov. #{self.id} de {self.monto}'
