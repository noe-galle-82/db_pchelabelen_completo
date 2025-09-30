from django.contrib import admin
from .models import Proveedores

@admin.register(Proveedores)
class ProveedoresAdmin(admin.ModelAdmin):
    # CORREGIDO: Usamos los nombres exactos de tu Proveedores models.py
    list_display = (
        'pk', 
        'nombre_proveedor',  # Corregido
        'localidad',         # Nuevo campo para list_display
        'teléfono'           # Corregido
    )
    
    # Campos que se pueden buscar
    search_fields = ('nombre_proveedor', 'localidad')
    
    # Campo para filtrar la lista
    list_filter = ('localidad',) # Filtra por un campoCharField sencillo