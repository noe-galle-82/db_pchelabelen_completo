from django.contrib import admin
from .models import TipoPago

@admin.register(TipoPago)
class TipoPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_tipo_pago')
    search_fields = ('nombre_tipo_pago',)
