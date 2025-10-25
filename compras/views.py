from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import CompraConLotesSerializer
from movimientos_caja.models import Caja, MovimientoDeCaja
from tipo_movimientos.models import TipoMovimiento
from tipo_pago.models import TipoPago

# Endpoint para registrar compra y lotes juntos
class RegistrarCompraView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		from .models import Compras, DetalleCompra
		from .serializers import CompraConLotesSerializer, DetalleCompraSerializer, CompraSerializer
		data = request.data.copy()
		lotes_data = data.pop('lotes', [])
		compra_serializer = CompraConLotesSerializer(data={**data, 'lotes': lotes_data}, context={'request': request})
		if compra_serializer.is_valid():
			compra = compra_serializer.save()
			detalles_creados = []
			# Crear los detalles de compra para cada lote
			for lote in compra.lotes.all():
				detalle_data = {
					'id_compra': compra.id,
					'id_lote': lote.id,
					'cantidad': lote.cantidad_inicial,
					'costo_unitario': lote.costo_unitario,
					'descuento_por_item': lote.descuento_por_item if hasattr(lote, 'descuento_por_item') else 0,
					'subtotal': (lote.cantidad_inicial * lote.costo_unitario) - (lote.descuento_por_item if hasattr(lote, 'descuento_por_item') else 0)
				}
				detalle_serializer = DetalleCompraSerializer(data=detalle_data)
				if detalle_serializer.is_valid():
					detalle_serializer.save()
					detalles_creados.append(detalle_serializer.data)
				else:
					return Response(detalle_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			# Registrar movimiento de caja tipo EGRESO
			caja = Caja.objects.filter(estado='ABIERTA').first()
			from core.models import EmpleadoProfile
			empleado_user = request.user
			empleado_profile = EmpleadoProfile.objects.get(user=empleado_user)
			tm = TipoMovimiento.objects.filter(nombre_tipo_movimiento__iexact='EGRESO').first()
			if not tm:
				tm = TipoMovimiento.objects.create(nombre_tipo_movimiento='EGRESO')
			tp = TipoPago.objects.filter(nombre_tipo_pago__iexact=data.get('medio_pago', 'EFECTIVO')).first()
			if not tp:
				tp = TipoPago.objects.create(nombre_tipo_pago=data.get('medio_pago', 'EFECTIVO'))
			MovimientoDeCaja.objects.create(
				caja=caja,
				monto=compra.monto_total,
				descripcion=f'Compra #{compra.id}',
				empleado=empleado_profile,
				id_tipo_movimiento=tm,
				id_tipo_pago=tp,
				tipo='EGRESO',
				origen='COMPRA',
				ref_type='compra',
				ref_id=compra.id,
				created_by=empleado_user,
			)
			response_data = CompraSerializer(compra).data
			response_data['detalles'] = detalles_creados
			return Response(response_data, status=status.HTTP_201_CREATED)
		return Response(compra_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
