from django.urls import path
from . import views

urlpatterns = [
    # URL principal para registrar una nueva venta: /ventas/registrar/
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    
    # URL de redirección después de un registro exitoso: /ventas/exito/
    path('exito/', views.venta_exitosa_placeholder, name='venta_exitosa'),
    
    # Añade aquí otras URLs relacionadas con Ventas (ej: listar, editar, eliminar)
]