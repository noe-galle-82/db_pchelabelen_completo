from django.contrib import admin
from .models import DetalleVenta 

# 1. CLASE INLINE (USADA DENTRO DE VENTAS/ADMIN.PY)
# Define el formulario para editar detalles dentro del formulario de Venta.
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    # CRUCIAL: 'id_lote' es obligatorio y debe estar aquí.
    fields = (
        'id_producto', 
        'id_lote',          
        'cantidad', 
        'precio_unitario', 
        'subtotal'
    )
    extra = 1

# 2. CLASE DE REGISTRO PRINCIPAL (Si accedes a DetalleVenta directamente)
@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = (
        'id_venta', 
        'id_producto', 
        'id_lote',          
        'cantidad', 
        'precio_unitario', 
        'subtotal'
    )
    # Campos que aparecen en el formulario de edición/creación
    fields = (
        'id_venta', 
        'id_producto', 
        'id_lote',          
        'cantidad', 
        'precio_unitario', 
        'subtotal'
    )