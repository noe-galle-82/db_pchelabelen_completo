from django.contrib import admin
from .models import Caja, MovimientoDeCaja

# --- Registro del Control de Caja (Apertura/Cierre) ---
@admin.register(Caja) 
class CajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'empleado_apertura', 'fecha_apertura', 'fecha_cierre')
    list_filter = ('estado', 'fecha_apertura')
    # Usar raw_id_fields para buscar empleados por ID/nombre de usuario
    raw_id_fields = ('empleado_apertura', 'empleado_cierre')
    
# --- Registro de Movimientos de Caja (Transacciones) ---
@admin.register(MovimientoDeCaja)
class MovimientoDeCajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'caja', 'empleado', 'monto', 'id_tipo_movimiento', 'id_tipo_pago', 'fecha_movimiento')
    list_filter = ('id_tipo_movimiento', 'id_tipo_pago', 'empleado', 'fecha_movimiento')
    search_fields = ('empleado__user__username', 'descripcion')
    raw_id_fields = ('caja', 'empleado', 'id_tipo_movimiento', 'id_tipo_pago')