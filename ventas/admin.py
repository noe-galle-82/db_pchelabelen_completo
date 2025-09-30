from django.contrib import admin
from .models import Venta 
# from detalles_venta.admin import DetalleVentaInline # Importar el Inline que ya definimos (COMENTADO TEMPORALMENTE)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    # 🚨 CORRECCIÓN: Asumo que el campo total se llama 'total_venta' para que funcione list_display y readonly_fields.
    list_display = (
        'pk',
        'fecha_venta',
        'total_venta', # Corregido de 'total'
        # Agrega aquí otros campos importantes de Venta si los tienes
    )
    
    fields = (
        'fecha_venta',
        'total_venta', # Corregido de 'total'
        # Agrega aquí otros campos de Venta que quieras editar
    )

    # Si quieres mostrar detalles inline, descomenta la siguiente línea
    # inlines = [DetalleVentaInline] # COMENTADO TEMPORALMENTE

    # 🚨 CORRECCIÓN: Usamos 'total_venta'
    readonly_fields = ('total_venta', 'fecha_venta') 

    # 🚨 CORRECCIÓN: Usar el nombre del campo real para el filtro.
    list_filter = ('fecha_venta',) 
    search_fields = ('pk',) 

