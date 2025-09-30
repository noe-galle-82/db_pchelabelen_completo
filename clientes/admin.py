from django.contrib import admin
from .models import Clientes 

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    # ¡CORREGIDO! Usando los nombres exactos: nombre_completo, teléfono
    list_display = ('usuario', 'nombre_completo', 'teléfono', 'email')
    
    # El campo que Django usa para filtrar debe ser un campo real del modelo.
    # Usamos 'nombre_completo' o 'email' para filtrar, ya que no hay campo 'apellido'
    list_filter = ('nombre_completo',)
    
    # Campos para la barra de búsqueda
    search_fields = ('nombre_completo', 'email', 'teléfono')
    
    # Los campos que aparecen en el formulario de edición.
    fields = ('usuario', 'nombre_completo', 'email', 'teléfono', 'direccion')
