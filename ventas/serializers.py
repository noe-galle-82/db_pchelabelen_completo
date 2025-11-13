
from rest_framework import serializers
from decimal import Decimal
from .models import Venta, DetalleVenta
from clientes.models import Clientes


class LoteAsignadoSerializer(serializers.Serializer):
    lote_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
    precio_unitario = serializers.DecimalField(max_digits=12, decimal_places=2)
    descuento_por_item = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)


class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = ['id', 'id_producto', 'id_lote', 'cantidad', 'precio_unitario', 'descuento_por_item', 'subtotal']


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    # Fecha y hora separadas para mejor UX
    fecha = serializers.SerializerMethodField()
    hora = serializers.SerializerMethodField()
    cliente = serializers.SerializerMethodField()
    movimiento_caja = serializers.SerializerMethodField()
    empleado_id = serializers.IntegerField(source='empleado.id', read_only=True)
    empleado_nombre = serializers.SerializerMethodField()
    # Campos financieros opcionales
    numero = serializers.CharField(read_only=True)
    bruto = serializers.SerializerMethodField()
    descuento_total = serializers.SerializerMethodField()
    recargo_total = serializers.SerializerMethodField()
    impuestos_total = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [
            'id', 'numero', 'fecha', 'hora', 'cliente', 'medio_pago', 'notas',
            'empleado_id', 'empleado_nombre',
            'monto_total', 'bruto', 'descuento_total', 'recargo_total', 'impuestos_total',
            'detalles', 'movimiento_caja'
        ]

    def get_cliente(self, obj):
        if not obj.cliente:
            return None
        return {
            'id': obj.cliente.id,
            'nombre_completo': f"{obj.cliente.nombre} {obj.cliente.apellido}",
            'email': obj.cliente.email,
        }

    def get_movimiento_caja(self, obj):
        # Este campo se completa en la vista via context (si existe)
        mc = self.context.get('movimiento_caja')
        return mc

    def get_fecha(self, obj):
        from django.utils import timezone
        dt = timezone.localtime(obj.fecha_venta)
        return dt.strftime("%d-%m-%Y")

    def get_hora(self, obj):
        from django.utils import timezone
        dt = timezone.localtime(obj.fecha_venta)
        return dt.strftime("%H:%M")

    def get_empleado_nombre(self, obj):
        if not getattr(obj, 'empleado', None):
            return None
        nombre = getattr(obj.empleado, 'nombre', '') or ''
        apellido = getattr(obj.empleado, 'apellido', '') or ''
        full = f"{nombre} {apellido}".strip()
        return full or str(obj.empleado)

    def _acum_financiero(self, obj):
        bruto_sum = Decimal('0.00')
        desc_sum = Decimal('0.00')
        for det in obj.detalles.all():
            lb = det.precio_unitario * det.cantidad
            bruto_sum += lb
            desc_sum += (lb - det.subtotal)
        return bruto_sum, desc_sum

    def get_bruto(self, obj):
        from decimal import Decimal
        bruto_sum, _ = self._acum_financiero(obj)
        return None if bruto_sum == Decimal('0.00') else bruto_sum

    def get_descuento_total(self, obj):
        from decimal import Decimal
        _, desc_sum = self._acum_financiero(obj)
        return None if desc_sum == Decimal('0.00') else desc_sum

    def get_recargo_total(self, obj):
        # No se gestiona en el modelo; devolver None para que el front lo trate como opcional
        return None

    def get_impuestos_total(self, obj):
        # No se gestiona en el modelo; devolver None para que el front lo trate como opcional
        return None


class VentaListSerializer(serializers.ModelSerializer):
    # Fecha y hora separadas para listado
    fecha = serializers.SerializerMethodField()
    hora = serializers.SerializerMethodField()
    total = serializers.DecimalField(source='monto_total', max_digits=12, decimal_places=2, read_only=True, coerce_to_string=False)
    medio_pago = serializers.CharField(read_only=True)
    numero = serializers.CharField(read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    empleado_id = serializers.IntegerField(source='empleado.id', read_only=True)
    empleado_nombre = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    bruto = serializers.SerializerMethodField()
    descuento_total = serializers.SerializerMethodField()
    recargo_total = serializers.SerializerMethodField()
    impuestos_total = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'hora', 'total', 'medio_pago', 'numero', 'cliente_nombre', 'empleado_id', 'empleado_nombre', 'items', 'bruto', 'descuento_total', 'recargo_total', 'impuestos_total']

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            nombre = getattr(obj.cliente, 'nombre', '') or ''
            apellido = getattr(obj.cliente, 'apellido', '') or ''
            full = f"{nombre} {apellido}".strip()
            return full or str(obj.cliente)
        return None

    def get_items(self, obj):
        # Espera prefetch de detalles__id_producto en la vista
        data = []
        for det in getattr(obj, 'detalles').all():
            prod_nombre = getattr(det.id_producto, 'nombre', None)
            data.append({
                'producto_nombre': prod_nombre,
                'cantidad': det.cantidad,
                'precio_unitario': float(det.precio_unitario) if det.precio_unitario is not None else None,
                'subtotal': float(det.subtotal) if det.subtotal is not None else None,
            })
        return data

    def get_empleado_nombre(self, obj):
        if not getattr(obj, 'empleado', None):
            return None
        nombre = getattr(obj.empleado, 'nombre', '') or ''
        apellido = getattr(obj.empleado, 'apellido', '') or ''
        full = f"{nombre} {apellido}".strip()
        return full or str(obj.empleado)

    def get_fecha(self, obj):
        from django.utils import timezone
        dt = timezone.localtime(obj.fecha_venta)
        return dt.strftime("%d-%m-%Y")

    def get_hora(self, obj):
        from django.utils import timezone
        dt = timezone.localtime(obj.fecha_venta)
        return dt.strftime("%H:%M")

    def _acum_financiero(self, obj):
        bruto_sum = Decimal('0.00')
        desc_sum = Decimal('0.00')
        for det in obj.detalles.all():
            lb = det.precio_unitario * det.cantidad
            bruto_sum += lb
            desc_sum += (lb - det.subtotal)
        return bruto_sum, desc_sum

    def get_bruto(self, obj):
        from decimal import Decimal
        bruto_sum, _ = self._acum_financiero(obj)
        return None if bruto_sum == Decimal('0.00') else float(bruto_sum)

    def get_descuento_total(self, obj):
        from decimal import Decimal
        _, desc_sum = self._acum_financiero(obj)
        return None if desc_sum == Decimal('0.00') else float(desc_sum)

    def get_recargo_total(self, obj):
        return None

    def get_impuestos_total(self, obj):
        return None


class VentaItemInputSerializer(serializers.Serializer):
    # Soporta snake y camelCase
    producto_id = serializers.IntegerField(required=True)
    lotes_asignados = LoteAsignadoSerializer(many=True, required=True)

    def validate(self, attrs):
        if not attrs.get('lotes_asignados'):
            raise serializers.ValidationError({'lotes_asignados': 'Debe ser una lista de lotes asignados y no puede estar vacía'})
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
        allowed = {'EFECTIVO', 'TRANSFERENCIA'}
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
