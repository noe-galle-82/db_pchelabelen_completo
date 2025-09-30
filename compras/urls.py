from django.urls import path
from . import views

urlpatterns = [
    # 1. URL principal para listar todas las compras (ej: /compras/)
    # Esta ruta llama a la vista 'listar_compras'
    path('', views.listar_compras, name='compras_listado'), 
    
    # 2. URL para registrar una nueva compra (ej: /compras/registrar/)
    path('registrar/', views.registrar_compra, name='registrar_compra'),
    
    # Hemos eliminado la ruta de 'exito/' para simplificar y evitar errores.
]
