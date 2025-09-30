from django.contrib import admin
from .models import Compras

# IMPORTANTE: Se necesita importar el Inline desde la app detalles_compra.
# Esto asume que la app detalles_compra existe y tiene su admin.py
from detalles_compra.admin import DetalleCompraInline 


@admin.register(Compras)
class ComprasAdmin(admin.ModelAdmin):
    # 'list_display' está bien, ya que solo muestra los valores
    list_display = (
        'pk', 
        'id_proveedor', 
        'id_empleado',      
        'fecha',            # Mostrar fecha (read-only)
        'total'             # Mostrar total (read-only)
    )
    
    # ¡CORRECCIÓN! Eliminamos 'fecha' y 'total' de 'fields' porque son auto_now_add o calculados
    fields = (
        'id_proveedor', 
        'id_empleado', 
        'id_tipo_pago', 
        # 'fecha' ELIMINADO: Django lo asigna automáticamente (auto_now_add=True)
        # 'total' ELIMINADO: Se calcula en la vista, no se edita directamente
    )

    inlines = [DetalleCompraInline]

    # ¡CORRECCIÓN! Declaramos 'fecha' y 'total' como de solo lectura
    readonly_fields = ('fecha', 'total',) 
    
    # Usamos los campos correctos para filtrar.
    list_filter = ('id_proveedor', 'id_empleado', 'fecha') 
    
    search_fields = ('id_proveedor__nombre', 'id_empleado__first_name', 'id_empleado__last_name') 
