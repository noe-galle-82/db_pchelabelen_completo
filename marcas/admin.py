from django.contrib import admin
from .models import Marca 

@admin.register(Marca) 
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre_marca',) 
    search_fields = ('nombre_marca',)