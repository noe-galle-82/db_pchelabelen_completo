from rest_framework import serializers
from .models import Lote

class LoteSerializer(serializers.ModelSerializer):
    costo_unitario_final = serializers.SerializerMethodField()
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Lote
        fields = [
            'id','producto','producto_nombre','numero_lote','cantidad_inicial','cantidad_disponible',
            'costo_unitario','descuento_tipo','descuento_valor','costo_unitario_final',
            'fecha_compra','fecha_vencimiento','proveedor','notas','creado'
        ]
        read_only_fields = ['id','creado','costo_unitario_final']
    
    def get_costo_unitario_final(self, obj):
        return obj.costo_unitario_final()

    def validate(self, attrs):
        cantidad_inicial = attrs.get('cantidad_inicial')
        cantidad_disponible = attrs.get('cantidad_disponible')
        if cantidad_disponible is not None and cantidad_inicial is not None and cantidad_disponible > cantidad_inicial:
            raise serializers.ValidationError('cantidad_disponible no puede ser mayor que cantidad_inicial')
        return attrs
