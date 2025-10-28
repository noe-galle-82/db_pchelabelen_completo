from django.urls import path
from .views import RegistrarCompraView  # o registrar_compra si usas función

urlpatterns = [
    path('registrar-compra/', RegistrarCompraView.as_view(), name='registrar-compra'),
]
