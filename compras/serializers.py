from .models import Compras, DetalleCompra
from rest_framework import serializers
from .models import Compras
from lotes.models import Lote

class DetalleCompraSerializer(serializers.ModelSerializer):
    producto = serializers.SerializerMethodField()

    def get_producto(self, obj):
        return {
            'id': obj.id_lote.producto.id,
            'nombre': obj.id_lote.producto.nombre
        } if obj.id_lote and obj.id_lote.producto else None

    class Meta:
        model = DetalleCompra
        fields = ['id', 'id_compra', 'id_lote', 'producto', 'cantidad', 'costo_unitario', 'descuento_por_item', 'subtotal']

class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True, read_only=True)

    class Meta:
        model = Compras
        fields = ['id', 'monto_total', 'fecha_compra', 'id_proveedor', 'id_usuario', 'detalles']
        read_only_fields = ['id', 'fecha_compra', 'id_usuario', 'detalles']

    def create(self, validated_data):
        user = self.context['request'].user
        return Compras.objects.create(id_usuario=user, **validated_data)

class LoteCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        exclude = ['id', 'compra', 'creado', 'activo']

class CompraConLotesSerializer(serializers.ModelSerializer):
    lotes = LoteCompraSerializer(many=True)

    class Meta:
        model = Compras
        fields = ['id', 'monto_total', 'fecha_compra', 'id_proveedor', 'id_usuario', 'lotes']
        read_only_fields = ['id', 'fecha_compra', 'id_usuario']

    def create(self, validated_data):
        lotes_data = validated_data.pop('lotes')
        user = self.context['request'].user
        compra = Compras.objects.create(id_usuario=user, **validated_data)
        for lote_data in lotes_data:
            Lote.objects.create(compra=compra, **lote_data)
        return compra
