from django.contrib import admin
from .models import Lotes

@admin.register(Lotes)
class LotesAdmin(admin.ModelAdmin):
    # list_display muestra los campos en la vista de lista del Admin
    list_display = (
        'pk',  
        'codigo_lote', 
        'id_producto',
        'cantidad_ingresada', # Cantidad que se compró originalmente
        'stock',              # Cantidad actual disponible
        'precio_costo_unitario'
    )
    
    # fields define los campos que se pueden editar en el formulario
    fields = (
        'id_producto',
        'codigo_lote', 
        'cantidad_ingresada', 
        'stock',
        'precio_costo_unitario'
    )
    
    # La búsqueda permite buscar por el código de lote o por el nombre del producto
    search_fields = ('codigo_lote', 'id_producto__nombre_producto')
    
    # Nota: No usamos list_filter porque no hay campos de fecha o booleanos para filtrar.

