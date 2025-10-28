from django.contrib import admin
from .models import Clientes


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "email", "teléfono", "dni", "condicion_iva", "activo")
    search_fields = ("nombre", "apellido", "email", "dni")
    list_filter = ("condicion_iva", "activo")
