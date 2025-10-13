from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from rest_framework.test import APIRequestFactory, force_authenticate

from core.models import Producto, EmpleadoProfile
from lotes.models import Lote
from movimientos_caja.models import Caja
from ventas.views import VentaViewSet


class Command(BaseCommand):
    help = "Ejecuta un flujo E2E: abre caja, crea producto y lote, registra una venta"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--password', type=str, default='admin1234')
        parser.add_argument('--opening', type=Decimal, default=Decimal('10000'))
        parser.add_argument('--precio', type=Decimal, default=Decimal('1500'))
        parser.add_argument('--cantidad', type=int, default=2)

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']
        opening = options['opening']
        precio = options['precio']
        cantidad = options['cantidad']

        user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
        if not user.check_password(password):
            user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Asegurar perfil (opcional)
        EmpleadoProfile.objects.get_or_create(user=user, defaults={'nombre_tipo_usuario': 'Gerente', 'numero_empleado': 'E2E001'})

        # Abrir caja del usuario si no existe
        caja = Caja.objects.filter(usuario=user, estado='ABIERTA').first()
        if not caja:
            caja = Caja.objects.create(usuario=user, empleado_apertura=None, monto_inicial=opening, estado='ABIERTA')

        # Crear producto y lote
        prod = Producto.objects.create(nombre='Producto E2E', precio=precio, cantidad=0)
        lote = Lote.objects.create(producto=prod, cantidad_inicial=10, cantidad_disponible=10, costo_unitario=Decimal('1000'))

        # Preparar request a VentaViewSet
        factory = APIRequestFactory()
        payload = {
            'medio_pago': 'EFECTIVO',
            'idempotency_key': 'e2e-venta-demo',
            'items': [
                {
                    'producto_id': prod.id,
                    'lote_id': lote.id,
                    'cantidad': cantidad,
                    'precio_unitario': str(precio),
                }
            ]
        }
        request = factory.post('/api/ventas/', payload, format='json')
        force_authenticate(request, user=user)
        view = VentaViewSet.as_view({'post': 'create'})
        response = view(request)

        self.stdout.write(self.style.SUCCESS(f"Status: {response.status_code}"))
        self.stdout.write(str(response.data))
