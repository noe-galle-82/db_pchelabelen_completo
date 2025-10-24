from rest_framework import serializers
from .models import Compras
from lotes.models import Lote

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
