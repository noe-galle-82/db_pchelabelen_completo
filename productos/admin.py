from django.contrib import admin
from .models import Productos

# Usamos la clase ProductosAdmin para configurar la visualización en el Admin
class ProductosAdmin(admin.ModelAdmin):
    # SIMPLIFICACIÓN EXTREMA: Solo mostramos la clave primaria y el nombre
    # Si estos fallan, el problema está en models.py.
    list_display = (
        'pk', 
        'nombre_producto', 
    )
    
    # Campo para buscar (probablemente funciona)
    search_fields = ('nombre_producto',)
    
    # Eliminamos list_filter por ahora, ya que las Foreign Keys fallan
    list_filter = []

# Registramos el modelo usando la clase de configuración definida
admin.site.register(Productos, ProductosAdmin)