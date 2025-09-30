from django.urls import path
from . import views

urlpatterns = [
    # Mapea la función registrar_venta a la URL /ventas/registrar/
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    
    # Mapea la función de éxito (a donde redirige después de guardar)
    path('exito/', views.venta_exitosa_placeholder, name='venta_exitosa'),
]