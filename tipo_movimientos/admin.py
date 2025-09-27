from django.contrib import admin
from .models import TipoMovimiento

@admin.register(TipoMovimiento)
class TipoMovimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_tipo_movimiento')
    search_fields = ('nombre_tipo_movimiento',)
