from django.contrib import admin
from .models import Clientes


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "email", "teléfono", "dni", "condicion_iva", "activo")
    search_fields = ("nombre_completo", "email", "dni")
    list_filter = ("condicion_iva", "activo")
