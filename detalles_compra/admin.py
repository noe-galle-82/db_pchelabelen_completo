from django.contrib import admin
from .models import DetalleCompra

# 1. CLASE INLINE (USADA DENTRO DE COMPRAS/ADMIN.PY)
# Define el formulario para editar detalles dentro del formulario de Compra.
class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    # CRUCIAL: 'id_lote' es obligatorio y debe estar aquí.
    fields = (
        'id_producto', 
        'id_lote',          
        'cantidad', 
        'costo_unitario', 
        'subtotal'
    )
    extra = 1

# 2. CLASE DE REGISTRO PRINCIPAL (Si accedes a DetalleCompra directamente)
@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = (
        'id_compra', 
        'id_producto', 
        'id_lote',          
        'cantidad', 
        'costo_unitario', 
        'subtotal'
    )
    # Campos que aparecen en el formulario de edición/creación
    fields = (
        'id_compra', 
        'id_producto', 
        'id_lote',          
        'cantidad', 
        'costo_unitario', 
        'subtotal'
    )