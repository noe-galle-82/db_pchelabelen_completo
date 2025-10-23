from django.contrib import admin
from .models import Clientes


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "email", "telefono", "dni", "condicion_iva", "activo")
    search_fields = ("nombre", "apellido", "email", "dni")
    list_filter = ("condicion_iva", "activo")

    def has_change_permission(self, request, obj=None):
        if obj and obj.id == 1:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.id == 1:
            return False
        return super().has_delete_permission(request, obj)
