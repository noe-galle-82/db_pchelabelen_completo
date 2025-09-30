from django.contrib import admin
from .models import Productos

# Usamos la clase ProductosAdmin para configurar la visualización en el Admin
@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    # CORRECCIÓN: Usamos 'nombre' en lugar de 'nombre_producto' para resolver el error E108.
    list_display = (
        'pk', 
        'nombre', 
    )
    
    # Campo para buscar
    search_fields = ('nombre',)
    
    # Eliminamos list_filter por ahora, ya que las Foreign Keys fallan
    list_filter = []