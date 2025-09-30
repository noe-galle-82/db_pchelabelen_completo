from django.contrib import admin
from .models import DetalleVenta 
from django.utils.html import format_html

# 1. CLASE INLINE (USADA DENTRO DE VENTAS/ADMIN.PY)
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    
    # Campos que realmente existen en el modelo (venta, producto, cantidad, precio_unitario)
    fields = (
        'producto', 
        # Si 'lote' es necesario, debe ser añadido al modelo DetalleVenta primero.
        'cantidad', 
        'precio_unitario', 
        'get_subtotal_display' # Muestra el subtotal calculado
    )
    readonly_fields = ('get_subtotal_display',) # Es de solo lectura
    extra = 1
    
    # Método para calcular el subtotal y mostrarlo
    def get_subtotal_display(self, obj):
        if obj.cantidad and obj.precio_unitario:
            subtotal = obj.cantidad * obj.precio_unitario
            return f"$ {subtotal:,.2f}"
        return "-"
    get_subtotal_display.short_description = 'Subtotal'


# 2. CLASE DE REGISTRO PRINCIPAL 
@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    # Usamos los nombres de los campos existentes: venta, producto, cantidad, precio_unitario
    list_display = (
        'venta', 
        'producto', 
        'cantidad', 
        'precio_unitario', 
        'get_subtotal_display' # Usamos el método calculado
    )
    # Campos que aparecen en el formulario de edición/creación
    fields = (
        'venta', 
        'producto', 
        'cantidad', 
        'precio_unitario', 
        'get_subtotal_display'
    )
    # Hacemos el subtotal de solo lectura, ya que es calculado
    readonly_fields = ('get_subtotal_display',)
    search_fields = ('venta__id', 'producto__nombre')

    # Reutilizamos el método de la clase Inline para calcular el subtotal
    def get_subtotal_display(self, obj):
        if obj.cantidad and obj.precio_unitario:
            subtotal = obj.cantidad * obj.precio_unitario
            return f"$ {subtotal:,.2f}"
        return "-"
    get_subtotal_display.short_description = 'Subtotal'
