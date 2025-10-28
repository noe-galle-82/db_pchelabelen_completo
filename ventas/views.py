from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Venta, DetalleVenta
from .serializers import VentaSerializer, VentaCreateSerializer
from core.models import EmpleadoProfile, Producto
from clientes.models import Clientes
from lotes.models import Lote
from movimientos_caja.models import Caja, MovimientoDeCaja
from tipo_movimientos.models import TipoMovimiento
from tipo_pago.models import TipoPago


class VentaViewSet(viewsets.GenericViewSet):
	permission_classes = [IsAuthenticated]

	def get_empleado(self, user):
		try:
			return EmpleadoProfile.objects.get(user=user)
		except EmpleadoProfile.DoesNotExist:
			return None

	def get_open_caja(self, user):
		return Caja.objects.filter(estado='ABIERTA').first()

	@transaction.atomic
	def create(self, request):
		data = request.data
		ser = VentaCreateSerializer(data=data)
		ser.is_valid(raise_exception=True)
		payload = ser.validated_data

		# Caja abierta requerida (ya que registraremos movimiento de caja)
		caja = self.get_open_caja(request.user)
		if not caja:
			return Response({"detail": "No hay sesión de caja abierta"}, status=409)

		empleado = self.get_empleado(request.user)

		# Idempotencia (si se envía)
		idem = payload.get('idempotency_key')
		if idem:
			existente = Venta.objects.filter(idempotency_key=idem).first()
			if existente:
				return Response(VentaSerializer(existente).data, status=200)

		# Resolver cliente (opcional)
		cliente = None
		cliente_id = payload.get('cliente_id')
		if cliente_id:
			cliente = Clientes.objects.filter(id=cliente_id).first()

		# Calcular totales y validar stock
		items = payload['items']
		detalles_creados = []
		total = Decimal('0.00')

		venta = Venta.objects.create(
			caja=caja,
			empleado=empleado,
			cliente=cliente,
			medio_pago=payload['medio_pago'],
			notas=payload.get('notas') or None,
			idempotency_key=idem or None,
			monto_total=Decimal('0.00'),
		)


		for it in items:
			producto = Producto.objects.get(id=it['producto_id'])
			lotes_asignados = it.get('lotes_asignados', [])
			if not lotes_asignados:
				raise serializers.ValidationError({"detail": f"No se especificaron lotes para el producto {producto.id}"})
			for lote_info in lotes_asignados:
				lote_id = lote_info['lote_id']
				cantidad = int(lote_info['cantidad'])
				precio_unitario = Decimal(str(lote_info['precio_unitario']))
				desc = Decimal(str(lote_info.get('descuento_por_item') or '0'))
				lote = Lote.objects.select_for_update().get(id=lote_id)
				if lote.cantidad_disponible < cantidad:
					raise serializers.ValidationError({"detail": f"Stock insuficiente en lote {lote_id} para producto {producto.id}"})
				subtotal = precio_unitario * Decimal(cantidad) * (Decimal('1.0') - desc / Decimal('100'))
				detalle = DetalleVenta.objects.create(
					id_venta=venta,
					id_producto=producto,
					id_lote=lote,
					cantidad=cantidad,
					precio_unitario=precio_unitario,
					descuento_por_item=desc if desc > 0 else None,
					subtotal=subtotal,
				)
				detalles_creados.append(detalle)
				total += subtotal
				# descontar stock
				lote.cantidad_disponible -= cantidad
				if lote.cantidad_disponible <= 0:
					lote.activo = False
				lote.save(update_fields=['cantidad_disponible', 'activo'])

		# Actualizar total de venta
		venta.monto_total = total
		venta.save(update_fields=['monto_total'])

		# Registrar movimiento de caja (INGRESO)
		tm = TipoMovimiento.objects.filter(nombre_tipo_movimiento__iexact='INGRESO').first()
		if not tm:
			tm = TipoMovimiento.objects.create(nombre_tipo_movimiento='INGRESO')
		tp = TipoPago.objects.filter(nombre_tipo_pago__iexact=payload['medio_pago']).first()
		if not tp:
			tp = TipoPago.objects.create(nombre_tipo_pago=payload['medio_pago'])
		mov = MovimientoDeCaja.objects.create(
			caja=caja,
			monto=total,
			descripcion=f'Venta #{venta.id}',
			empleado=empleado,
			id_tipo_movimiento=tm,
			id_tipo_pago=tp,
			tipo='INGRESO',
			origen='VENTA',
			ref_type='venta',
			ref_id=venta.id,
			created_by=request.user,
		)
		mov_slim = {"id": mov.id, "tipo": "INGRESO", "medio_pago": payload['medio_pago'], "monto": float(total)}
		return Response(VentaSerializer(venta, context={'movimiento_caja': mov_slim}).data, status=201)

