from rest_framework import serializers
from .models import Proveedores

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedores
        fields = ['id', 'nombre', 'contacto', 'telefono', 'email', 'direccion', 'localidad', 'cuil', 'notas', 'activo']
        extra_kwargs = {
            'activo': {'required': False, 'default': True}
        }