from django.urls import path
from .views import RegistrarCompraView

urlpatterns = [
    path('api/registrar-compra/', RegistrarCompraView.as_view(), name='registrar-compra'),
]
