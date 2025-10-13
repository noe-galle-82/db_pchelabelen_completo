from rest_framework import viewsets, status, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from .models import Caja, MovimientoDeCaja
from .serializers import CajaSerializer, MovimientoDeCajaSerializer
from core.models import EmpleadoProfile
from tipo_movimientos.models import TipoMovimiento
from tipo_pago.models import TipoPago


class CajaViewSet(viewsets.ModelViewSet):
	queryset = Caja.objects.all().order_by('-fecha_apertura')
	serializer_class = CajaSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = [filters.SearchFilter]
	search_fields = ['estado']

	def get_empleado(self, user):
		try:
			return EmpleadoProfile.objects.get(user=user)
		except EmpleadoProfile.DoesNotExist:
			return None

	def is_gerente(self, user):
		# Chequea si el usuario pertenece al grupo "Gerente"
		return user.groups.filter(name__iexact='Gerente').exists()

	def get_queryset(self):
		qs = super().get_queryset()
		if self.is_gerente(self.request.user):
			return qs
		# Usuarios no gerente: solo sus sesiones
		return qs.filter(usuario=self.request.user)

	@action(detail=False, methods=['get'])
	def sesion_abierta(self, request):
		# Sesión por usuario
		caja = Caja.objects.filter(usuario=request.user, estado='ABIERTA').first()
		if not caja:
			return Response({"open": False}, status=status.HTTP_200_OK)
		data = self.get_serializer(caja).data
		data["open"] = True
		return Response(data)

	@action(detail=False, methods=['post'])
	@transaction.atomic
	def abrir(self, request):
		empleado = self.get_empleado(request.user)
		if Caja.objects.filter(usuario=request.user, estado='ABIERTA').exists():
			return Response({"detail": "Ya hay una sesión de caja abierta para este usuario."}, status=409)
		# Aceptar snake y camelCase
		opening_amount = (
			request.data.get('opening_amount')
			or request.data.get('openingAmount')
			or request.data.get('monto_inicial')
		)
		if opening_amount is None:
			return Response({"detail": "opening_amount es requerido"}, status=400)
		caja = Caja.objects.create(
			empleado_apertura=empleado,
			usuario=request.user,
			monto_inicial=opening_amount,
			estado='ABIERTA'
		)
		data = self.get_serializer(caja).data
		data["open"] = True
		return Response(data, status=201)

	@action(detail=False, methods=['post'])
	@transaction.atomic
	def cerrar(self, request):
		empleado = self.get_empleado(request.user)
		caja = Caja.objects.filter(usuario=request.user, estado='ABIERTA').first()
		if not caja:
			return Response({"detail": "No hay sesión abierta"}, status=409)
		# Aceptar snake y camelCase
		counted = (
			request.data.get('counted_amount')
			or request.data.get('countedAmount')
			or request.data.get('closing_counted_amount')
		)
		if counted is None:
			return Response({"detail": "counted_amount es requerido"}, status=400)
		# Calcular saldo del sistema
		system_amount = caja.saldo_actual
		diff = float(counted) - float(system_amount)
		caja.closing_counted_amount = counted
		caja.closing_system_amount = system_amount
		caja.difference_amount = diff
		caja.estado = 'CERRADA'
		caja.fecha_cierre = timezone.now()
		caja.empleado_cierre = empleado
		caja.save()

		# Si hay diferencia, registrar ajuste
		difference_movement = None
		if diff != 0:
			tipo_mov, _ = TipoMovimiento.objects.get_or_create(nombre_tipo_movimiento='Ajuste de Cierre')
			efectivo, _ = TipoPago.objects.get_or_create(nombre_tipo_pago='EFECTIVO')
			difference_movement = MovimientoDeCaja.objects.create(
				caja=caja,
				monto=abs(diff),
				descripcion='Ajuste por diferencia de cierre',
				empleado=empleado,
				id_tipo_movimiento=tipo_mov,
				id_tipo_pago=efectivo,
				tipo='AJUSTE',
				origen='CIERRE',
				ref_type='caja',
				ref_id=caja.id,
			)
		resp = self.get_serializer(caja).data
		resp["open"] = False
		if difference_movement:
			resp['difference_movement'] = MovimientoDeCajaSerializer(difference_movement).data
		return Response(resp)

	@action(detail=False, methods=['get'])
	def catalogos(self, request):
		# Endpoint auxiliar (Opción B) para devolver mapeos nombre -> id
		from tipo_movimientos.models import TipoMovimiento
		from tipo_pago.models import TipoPago
		tipos_mov = [
			{"id": tm.id, "nombre": tm.nombre_tipo_movimiento.upper()}
			for tm in TipoMovimiento.objects.all().order_by('id')
		]
		tipos_pago = [
			{"id": tp.id, "nombre": tp.nombre_tipo_pago.upper()}
			for tp in TipoPago.objects.all().order_by('id')
		]
		return Response({"tipos_movimiento": tipos_mov, "tipos_pago": tipos_pago})


class MovimientoDeCajaViewSet(viewsets.ModelViewSet):
	queryset = MovimientoDeCaja.objects.all().order_by('-created_at')
	serializer_class = MovimientoDeCajaSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ['caja', 'origen', 'ref_type', 'ref_id']
	search_fields = ['origen', 'ref_type']

	def get_empleado(self, user):
		try:
			return EmpleadoProfile.objects.get(user=user)
		except EmpleadoProfile.DoesNotExist:
			return None

	def is_gerente(self, user):
		return user.groups.filter(name__iexact='Gerente').exists()

	def get_queryset(self):
		qs = super().get_queryset().select_related('caja')
		if self.is_gerente(self.request.user):
			return qs
		return qs.filter(caja__usuario=self.request.user)

	def list(self, request, *args, **kwargs):
		# Si no es gerente y pide una caja que no es suya, 403
		caja_id = request.query_params.get('caja')
		if caja_id and not self.is_gerente(request.user):
			try:
				caja = Caja.objects.get(id=caja_id)
				if caja.usuario_id != request.user.id:
					return Response({"detail": "No tenés permisos para ver estos movimientos"}, status=status.HTTP_403_FORBIDDEN)
			except Caja.DoesNotExist:
				pass  # devolverá lista vacía de todas formas
		return super().list(request, *args, **kwargs)

	def perform_create(self, serializer):
		empleado = self.get_empleado(self.request.user)
		# Opción C: permitir omitir "caja" y tomar la sesión abierta del usuario
		caja_id = self.request.data.get('caja')
		caja = None
		if caja_id:
			caja = Caja.objects.filter(id=caja_id).first()
		else:
			caja = Caja.objects.filter(usuario=self.request.user, estado='ABIERTA').first()
		if not caja:
			raise serializers.ValidationError({"detail": "No hay sesión abierta para registrar movimientos"})
		# Seguridad: si no es gerente, solo puede registrar en su propia caja
		if (not self.is_gerente(self.request.user)) and caja.usuario_id != self.request.user.id:
			raise serializers.ValidationError({"detail": "No tenés permisos para registrar en esta caja"})

		# Opción A: aceptar strings en medio_pago y tipo_movimiento (aceptar camelCase)
		medio_pago = self.request.data.get('medio_pago') or self.request.data.get('medioPago')
		id_tipo_pago = self.request.data.get('id_tipo_pago')
		if medio_pago and isinstance(medio_pago, str) and not medio_pago.isdigit():
			mp = TipoPago.objects.filter(nombre_tipo_pago__iexact=medio_pago).first()
			if not mp:
				mp = TipoPago.objects.create(nombre_tipo_pago=medio_pago.upper())
			id_tipo_pago = mp.id
		elif not id_tipo_pago:
			efectivo, _ = TipoPago.objects.get_or_create(nombre_tipo_pago='EFECTIVO')
			id_tipo_pago = efectivo.id
		# Resolver instancia FK
		mp_obj = TipoPago.objects.filter(id=id_tipo_pago).first()

		tipo_movimiento = self.request.data.get('tipo_movimiento') or self.request.data.get('tipoMovimiento')
		id_tipo_movimiento = self.request.data.get('id_tipo_movimiento')
		if tipo_movimiento and isinstance(tipo_movimiento, str) and not tipo_movimiento.isdigit():
			tm = TipoMovimiento.objects.filter(nombre_tipo_movimiento__iexact=tipo_movimiento).first()
			if not tm:
				tm = TipoMovimiento.objects.create(nombre_tipo_movimiento=tipo_movimiento.upper())
			id_tipo_movimiento = tm.id
		elif not id_tipo_movimiento:
			tm, _ = TipoMovimiento.objects.get_or_create(nombre_tipo_movimiento='Movimiento de Caja')
			id_tipo_movimiento = tm.id
		# Resolver instancia FK
		tm_obj = TipoMovimiento.objects.filter(id=id_tipo_movimiento).first()

		# Normalizar claves de referencia y origen desde camelCase (antes de deducir tipo)
		ref_type = self.request.data.get('ref_type') or self.request.data.get('refType')
		ref_id = self.request.data.get('ref_id') or self.request.data.get('refId')
		origen = self.request.data.get('origen') or self.request.data.get('origin')
		if isinstance(origen, str):
			origen = origen.upper()

		# Determinar tipo efectivo: usa 'tipo' si viene, sino deriva de 'tipo_movimiento'
		tipo = self.request.data.get('tipo')
		if not tipo and isinstance(tipo_movimiento, str):
			tipo = tipo_movimiento.upper()
		# Intento de deducción por origen/ref_type si aún no hay tipo
		if not tipo:
			if isinstance(origen, str):
				if origen == 'COMPRA':
					tipo = 'EGRESO'
				elif origen == 'VENTA':
					tipo = 'INGRESO'
			elif isinstance(ref_type, str):
				low = ref_type.lower()
				if low == 'compra':
					tipo = 'EGRESO'
				elif low == 'venta':
					tipo = 'INGRESO'
		allowed_tipos = {'INGRESO','EGRESO','AJUSTE','REVERSO'}
		if tipo and tipo.upper() not in allowed_tipos:
			tipo = None

		# Validar ajuste_sign cuando tipo=AJUSTE
		ajuste_sign = self.request.data.get('ajuste_sign')
		if tipo == 'AJUSTE' and ajuste_sign not in ('IN', 'OUT'):
			raise serializers.ValidationError({"detail": "ajuste_sign requerido: IN|OUT para tipo=AJUSTE"})
		# Construir kwargs evitando pasar tipo=None (que rompe default del modelo)
		kwargs = dict(
			caja=caja,
			empleado=empleado,
			created_by=self.request.user,
			id_tipo_pago=mp_obj,
			id_tipo_movimiento=tm_obj,
			ajuste_sign=ajuste_sign,
			ref_type=ref_type,
			ref_id=ref_id,
			origen=origen
		)
		if tipo:
			kwargs['tipo'] = tipo
		return serializer.save(**kwargs)

	@action(detail=False, methods=['post'])
	@transaction.atomic
	def reversar(self, request):
		# Solo Gerente
		if not self.is_gerente(request.user):
			return Response({"detail": "No tenés permisos para esta acción"}, status=status.HTTP_403_FORBIDDEN)
		empleado = self.get_empleado(request.user)
		mov_id = request.data.get('movement_id')
		if not mov_id:
			return Response({"detail": "movement_id es requerido"}, status=400)
		original = MovimientoDeCaja.objects.filter(id=mov_id).first()
		if not original:
			return Response({"detail": "Movimiento no encontrado"}, status=404)
		if original.status == 'REVERTED':
			return Response({"detail": "Ya fue revertido"}, status=409)
		efectivo, _ = TipoPago.objects.get_or_create(nombre_tipo_pago='EFECTIVO')
		tipo_mov, _ = TipoMovimiento.objects.get_or_create(nombre_tipo_movimiento='Reverso')
		caja = original.caja
		reason = request.data.get('reason')
		desc = f'Reverso de movimiento #{original.id}' + (f' - Motivo: {reason}' if reason else '')
		reverso = MovimientoDeCaja.objects.create(
			caja=caja,
			monto=original.monto,
			descripcion=desc,
			empleado=empleado,
			created_by=request.user,
			id_tipo_movimiento=tipo_mov,
			id_tipo_pago=efectivo,
			tipo='REVERSO',
			origen=original.origen,
			ref_type=original.ref_type,
			ref_id=original.ref_id,
			reversed_of=original,
			reversado_por=None
		)
		original.status = 'REVERTED'
		original.reversado_por = reverso
		original.save()
		return Response(MovimientoDeCajaSerializer(reverso).data, status=201)

