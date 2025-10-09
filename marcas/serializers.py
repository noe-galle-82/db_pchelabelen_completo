from rest_framework import serializers
from .models import Marca

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['id', 'nombre_marca', 'notas']
