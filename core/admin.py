from django.contrib import admin
from .models import EmpleadoProfile, Empleados
from django.contrib.auth.models import User

@admin.register(EmpleadoProfile) 
class EmpleadoProfileAdmin(admin.ModelAdmin):
    # ----------------------------------------------------
    # MÉTODOS CALCULADOS PARA EVITAR ERRORES E108
    # ----------------------------------------------------

    def nombre_empleado(self, obj):
        # Accede al nombre a través del modelo Empleados
        return f"{obj.empleado.nombre} {obj.empleado.apellido}"
    nombre_empleado.short_description = 'Nombre del Empleado'
    
    def nombre_usuario_django(self, obj):
        # Accede al nombre de usuario de Django a través de Empleados
        if obj.empleado.user:
            return obj.empleado.user.username
        return "N/A"
    nombre_usuario_django.short_description = 'Usuario (Django)'

    def numero_empleado(self, obj):
        # Usamos el DNI como número de empleado, asumiendo que es el identificador único
        return obj.empleado.dni
    numero_empleado.short_description = 'DNI/Código'

    # ----------------------------------------------------
    # CONFIGURACIÓN DEL ADMIN
    # ----------------------------------------------------
    
    # list_display ahora usa campos reales ('empleado', 'salario', 'direccion') 
    # y los nuevos métodos calculados.
    list_display = (
        'nombre_empleado',         # Método
        'nombre_usuario_django',   # Método
        'numero_empleado',         # Método (DNI)
        'salario',                 # Campo real
        'created_at',
    )
    
    # search_fields: Buscamos en los campos de las relaciones
    search_fields = (
        'empleado__nombre', 
        'empleado__apellido', 
        'empleado__dni',
        'empleado__user__username'
    )
    
    # raw_id_fields usa el campo ForeignKey/OneToOneField real: 'empleado' (no 'user')
    raw_id_fields = ('empleado',)

    # Campos que se pueden editar en el formulario
    fields = (
        'empleado', 
        'salario', 
        'direccion',
    )
