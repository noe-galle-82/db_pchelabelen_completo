from django.contrib import admin
from .models import Venta, DetalleVenta

# Clase Inline para ver los detalles dentro de la venta
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0 # No muestra filas extra vacías

# --- Registro de Venta ---
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_venta', 'empleado', 'caja', 'monto_total')
    list_filter = ('fecha_venta', 'empleado')
    search_fields = ('empleado__user__username',)
    # Muestra los detalles de la venta en la misma página
    inlines = [DetalleVentaInline] 
    raw_id_fields = ('caja', 'empleado') 

# No necesitamos registrar DetalleVenta por separado si usamos Inline, pero lo hacemos por si acaso.
# @admin.register(DetalleVenta)
# class DetalleVentaAdmin(admin.ModelAdmin):
#     list_display = ('id_venta', 'id_producto', 'cantidad', 'precio_unitario')
#     raw_id_fields = ('id_venta',)


