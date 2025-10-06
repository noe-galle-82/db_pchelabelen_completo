from django.contrib import admin
from .models import EmpleadoProfile, Producto

@admin.register(EmpleadoProfile) 
class EmpleadoProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre_tipo_usuario', 'numero_empleado') 
    search_fields = ('user__username', 'numero_empleado')
    # Permite navegar directamente al usuario de Django
    raw_id_fields = ('user',)

@admin.register(Producto) 
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'cantidad', 'categoria', 'creado') 
    list_filter = ('categoria', 'creado')
    search_fields = ('nombre', 'categoria')
    ordering = ('-creado',)
    readonly_fields = ('creado',)
