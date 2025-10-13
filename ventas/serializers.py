from rest_framework import serializers
from .models import Venta, DetalleVenta
from clientes.models import Clientes


class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = ['id', 'id_producto', 'id_lote', 'cantidad', 'precio_unitario', 'descuento_por_item', 'subtotal']


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    fecha = serializers.DateTimeField(source='fecha_venta', read_only=True)
    cliente = serializers.SerializerMethodField()
    movimiento_caja = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = ['id', 'numero', 'fecha', 'cliente', 'medio_pago', 'notas', 'monto_total', 'detalles', 'movimiento_caja']

    def get_cliente(self, obj):
        if not obj.cliente:
            return None
        return {
            'id': obj.cliente.usuario_id,
            'nombre_completo': obj.cliente.nombre_completo,
            'email': obj.cliente.email,
        }

    def get_movimiento_caja(self, obj):
        # Este campo se completa en la vista via context (si existe)
        mc = self.context.get('movimiento_caja')
        return mc


class VentaItemInputSerializer(serializers.Serializer):
    # Soporta snake y camelCase
    producto_id = serializers.IntegerField(required=False)
    productoId = serializers.IntegerField(required=False)
    lote_id = serializers.IntegerField(required=False, allow_null=True)
    loteId = serializers.IntegerField(required=False, allow_null=True)
    cantidad = serializers.IntegerField(min_value=1)
    precio_unitario = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    precioUnitario = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    descuento_por_item = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    descuentoPorItem = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    def validate(self, attrs):
        # Normalizar a snake_case
        if 'producto_id' not in attrs and 'productoId' in attrs:
            attrs['producto_id'] = attrs.pop('productoId')
        if 'lote_id' not in attrs and 'loteId' in attrs:
            attrs['lote_id'] = attrs.pop('loteId')
        if 'precio_unitario' not in attrs and 'precioUnitario' in attrs:
            attrs['precio_unitario'] = attrs.pop('precioUnitario')
        if 'descuento_por_item' not in attrs and 'descuentoPorItem' in attrs:
            attrs['descuento_por_item'] = attrs.pop('descuentoPorItem')
        return attrs


class VentaCreateSerializer(serializers.Serializer):
    # Soporta snake y camelCase
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
        # Normalizar a snake_case niveles superiores
        if 'cliente_id' not in attrs and 'clienteId' in attrs:
            attrs['cliente_id'] = attrs.pop('clienteId')
        mp = attrs.get('medio_pago') or attrs.get('medioPago')
        if 'medio_pago' not in attrs and 'medioPago' in attrs:
            attrs['medio_pago'] = attrs.pop('medioPago')
        if 'idempotency_key' not in attrs and 'idempotencyKey' in attrs:
            attrs['idempotency_key'] = attrs.pop('idempotencyKey')
        # Validar medio_pago normalizado
        if 'medio_pago' in attrs:
            attrs['medio_pago'] = self.validate_medio_pago(attrs['medio_pago'])
        else:
            raise serializers.ValidationError({'medio_pago': 'Este campo es requerido'})
        return attrs
