from django.db import models
from django.contrib.auth.models import User
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
        verbose_name='Empleado Apertura',
        null=True, blank=True
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
    # Campos de cierre y control
    closing_counted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    closing_system_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    difference_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Cajas"
        permissions = [
            ("can_open_cash_register", "Puede abrir y cerrar la caja"),
        ]

    def __str__(self):
        return f"Caja N°{self.pk} - {self.estado}"

    def _apply_effect(self, current, mov, factor=1):
        # factor permite invertir para REVERSO
        if mov.tipo == 'INGRESO':
            return current + (mov.monto * factor)
        if mov.tipo == 'EGRESO':
            return current - (mov.monto * factor)
        if mov.tipo == 'AJUSTE':
            if mov.ajuste_sign == 'IN':
                return current + (mov.monto * factor)
            if mov.ajuste_sign == 'OUT':
                return current - (mov.monto * factor)
        return current

    @property
    def saldo_total(self):
        saldo = self.monto_inicial
        for m in self.movimientos.all():
            if m.tipo == 'REVERSO' and m.reversed_of:
                # Aplica efecto inverso del original
                saldo = self._apply_effect(saldo, m.reversed_of, factor=-1)
            else:
                saldo = self._apply_effect(saldo, m)
        return saldo

    @property
    def saldo_efectivo(self):
        saldo = self.monto_inicial
        for m in self.movimientos.select_related('id_tipo_pago').all():
            nombre_mp = (m.id_tipo_pago.nombre_tipo_pago if m.id_tipo_pago else '').upper()
            afecta_caja = (nombre_mp == 'EFECTIVO')
            if not afecta_caja:
                # Solo contamos efectivo aquí; REVERSO también solo si original afectaba caja
                if m.tipo == 'REVERSO' and m.reversed_of:
                    orig_mp = (m.reversed_of.id_tipo_pago.nombre_tipo_pago if m.reversed_of.id_tipo_pago else '').upper()
                    if orig_mp == 'EFECTIVO':
                        saldo = self._apply_effect(saldo, m.reversed_of, factor=-1)
                continue
            # Afecta caja (EFECTIVO)
            if m.tipo == 'REVERSO' and m.reversed_of:
                saldo = self._apply_effect(saldo, m.reversed_of, factor=-1)
            else:
                saldo = self._apply_effect(saldo, m)
        return saldo

    @property
    def saldo_actual(self):
        # Alias para compatibilidad: igual a saldo_total
        return self.saldo_total


# ==========================================================
# 2. MODELO MOVIMIENTOS_DE_CAJA (Transacciones - Basado en el DER)
# ==========================================================
class MovimientoDeCaja(models.Model):
    # Referencia obligatoria a la CAJA que está abierta
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name='movimientos')
    
    # Atributos de tu DER
    fecha_movimiento = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    # REFERENCIAS CORREGIDAS: 
    # id_usuario ahora es empleado (usando EmpleadoProfile)
    empleado = models.ForeignKey(
        EmpleadoProfile, 
        on_delete=models.PROTECT, 
        verbose_name='Empleado',
        null=True, blank=True
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

    # Nuevos campos para MVP de Caja
    TIPOS = (
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
        ('AJUSTE', 'Ajuste'),
        ('REVERSO', 'Reverso'),
    )
    tipo = models.CharField(max_length=10, choices=TIPOS, default='INGRESO')

    ORIGENES = (
        ('VENTA', 'Venta'),
        ('COMPRA', 'Compra'),
        ('DEVOLUCION', 'Devolución'),
        ('APERTURA', 'Apertura'),
        ('CIERRE', 'Cierre'),
        ('MANUAL', 'Manual'),
        ('AJUSTE_MANUAL', 'Ajuste Manual'),
    )
    origen = models.CharField(max_length=20, choices=ORIGENES, blank=True, null=True)

    ref_type = models.CharField(max_length=30, blank=True, null=True)
    ref_id = models.IntegerField(blank=True, null=True)

    # Nuevo: quién creó el movimiento
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='movimientos_caja', null=True, blank=True)

    # Nuevo: signo del ajuste (para tipo=AJUSTE)
    AJUSTE_SIGN = (
        ('IN', 'Ingreso'),
        ('OUT', 'Egreso'),
    )
    ajuste_sign = models.CharField(max_length=3, choices=AJUSTE_SIGN, blank=True, null=True)

    STATUS = (
        ('NORMAL', 'Normal'),
        ('REVERTED', 'Revertido'),
    )
    status = models.CharField(max_length=10, choices=STATUS, default='NORMAL')
    # Nuevo: relación al movimiento original al que revierte (más útil para cálculo de saldo)
    reversed_of = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reversos')
    # Campo legado (puede quedar para compatibilidad)
    reversado_por = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reversa_de')
    
    class Meta:
        verbose_name_plural = "Movimientos de Caja"

    def __str__(self):
        return f'Mov. #{self.id} de {self.monto}'

    @property
    def es_ingreso(self):
        return self.tipo == 'INGRESO'
