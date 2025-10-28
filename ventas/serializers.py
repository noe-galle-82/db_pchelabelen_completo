from rest_framework import serializers
from .models import Venta, DetalleVenta
from clientes.models import Clientes


# ----------------------------------------------------------------------
# Serializador para los lotes asignados (dentro de cada ítem de venta)
# ----------------------------------------------------------------------
class LoteAsignadoSerializer(serializers.Serializer):
    lote_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
    precio_unitario = serializers.DecimalField(max_digits=12, decimal_places=2)
    # 👇 Este cambio asegura que si no se envía descuento, use 0
    descuento_por_item = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        required=False, allow_null=True, default=0
    )


# ----------------------------------------------------------------------
# Detalle de venta (cada producto vendido)
# ----------------------------------------------------------------------
class DetalleVentaSerializer(serializers.ModelSerializer):
    # 👇 También acá por si la creación se hace vía ModelSerializer
    descuento_por_item = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        required=False, allow_null=True, default=0
    )

    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'id_producto', 'id_lote', 'cantidad',
            'precio_unitario', 'descuento_por_item', 'subtotal'
        ]


# ----------------------------------------------------------------------
# Venta completa (lectura)
# ----------------------------------------------------------------------
class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    fecha = serializers.DateTimeField(source='fecha_venta', read_only=True)
    cliente = serializers.SerializerMethodField()
    movimiento_caja = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [
            'id', 'numero', 'fecha', 'cliente', 'medio_pago',
            'notas', 'monto_total', 'detalles', 'movimiento_caja'
        ]

    def get_cliente(self, obj):
        """Devuelve los datos básicos del cliente asociado a la venta"""
        if not obj.cliente:
            return None
        return {
            'id': obj.cliente.id,
            'nombre_completo': f"{obj.cliente.nombre} {obj.cliente.apellido}",
            'email': obj.cliente.email,
        }

    def get_movimiento_caja(self, obj):
        """Este campo se completa desde el contexto si existe"""
        return self.context.get('movimiento_caja')


# ----------------------------------------------------------------------
# Entrada de ítems de venta (cuando se crea una venta nueva)
# ----------------------------------------------------------------------
class VentaItemInputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(required=True)
    lotes_asignados = LoteAsignadoSerializer(many=True, required=True)

    def validate(self, attrs):
        if not attrs.get('lotes_asignados'):
            raise serializers.ValidationError({
                'lotes_asignados': 'Debe ser una lista de lotes asignados y no puede estar vacía'
            })
        return attrs


# ----------------------------------------------------------------------
# Creación de venta (API POST /api/ventas/)
# ----------------------------------------------------------------------
class VentaCreateSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField(required=False, allow_null=True)
    clienteId = serializers.IntegerField(required=False, allow_null=True)
    items = VentaItemInputSerializer(many=True)
    medio_pago = serializers.CharField(required=False)
    medioPago = serializers.CharField(required=False)
    notas = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    idempotencyKey = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_medio_pago(self, value):
        v = (value or '').strip().upper()
        allowed = {'EFECTIVO', 'TARJETA', 'TRANSFERENCIA', 'CREDITO'}
        if v not in allowed:
            raise serializers.ValidationError('medio_pago inválido')
        return v

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('items no puede estar vacío')
        return items

    def validate(self, attrs):
        # Normalizar nombres camelCase → snake_case
        if 'cliente_id' not in attrs and 'clienteId' in attrs:
            attrs['cliente_id'] = attrs.pop('clienteId')

        if 'medio_pago' not in attrs and 'medioPago' in attrs:
            attrs['medio_pago'] = attrs.pop('medioPago')

        if 'idempotency_key' not in attrs and 'idempotencyKey' in attrs:
            attrs['idempotency_key'] = attrs.pop('idempotencyKey')

        # Validar medio_pago
        mp = attrs.get('medio_pago')
        if not mp:
            raise serializers.ValidationError({'medio_pago': 'Este campo es requerido'})
        attrs['medio_pago'] = self.validate_medio_pago(mp)

        return attrs