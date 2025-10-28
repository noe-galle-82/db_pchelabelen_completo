from django.contrib import admin
from .models import EmpleadoProfile, Producto

# ===============================
# Admin Empleados
# ===============================
@admin.register(EmpleadoProfile)
class EmpleadoProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_nombre_tipo_usuario', 'numero_empleado', 'activo')
    list_filter = ('activo',)  # Solo campos reales, no properties
    search_fields = ('user__username', 'numero_empleado', 'user__email')
    raw_id_fields = ('user',)
    ordering = ('numero_empleado',)

    actions = ['marcar_activo', 'marcar_inactivo']

    # Mostrar el grupo del usuario en list_display
    def get_nombre_tipo_usuario(self, obj):
        groups = obj.user.groups.all()
        return groups[0].name if groups else None
    get_nombre_tipo_usuario.short_description = "Tipo Usuario"

    # Acciones personalizadas
    def marcar_activo(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f"{updated} empleado(s) marcado(s) como activo.")
    marcar_activo.short_description = "Marcar empleados seleccionados como activo"

    def marcar_inactivo(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f"{updated} empleado(s) marcado(s) como inactivo.")
    marcar_inactivo.short_description = "Marcar empleados seleccionados como inactivo"


# ===============================
# Admin Productos
# ===============================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'cantidad', 'categoria', 'creado')
    list_filter = ('categoria', 'creado')
    search_fields = ('nombre', 'categoria')
    ordering = ('-creado',)
    readonly_fields = ('creado',)
