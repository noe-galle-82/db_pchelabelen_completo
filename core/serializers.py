from django.contrib.auth.models import User, Group
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Producto
from productos.models import Categoria


class UserSerializer(ModelSerializer):
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]
        extra_kwargs = {"password": {"write_only": True, "allow_null": True, "required": False}}

    def get_role(self, obj):
        """Convierte el primer grupo del usuario a string"""
        return obj.groups.first().name if obj.groups.exists() else None

    def create(self, validated_data):
        """Crear usuario y asignar rol/grupo"""
        password = validated_data.pop("password")
        role = self.initial_data.get("role")  # Obtiene el rol del JSON enviado
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Asignar el grupo/rol si se proporcionó
        if role:
            try:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass  # Si el grupo no existe, lo ignoramos
        
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        role = self.initial_data.get("role")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if role:
            instance.groups.clear()
            group = Group.objects.get(name=role)
            instance.groups.add(group)

        return instance
    
class CategoriaMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

class ProductoSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(use_url=True, required=False)
    categoria_id = serializers.PrimaryKeyRelatedField(
        source='categoria_ref', queryset=Categoria.objects.all(), allow_null=True, required=False
    )
    categoria_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'precio', 'cantidad',
            'categoria',          # legacy texto (temporal)
            'categoria_id',       # FK writable
            'categoria_nombre',   # derivado
            'imagen', 'creado'
        ]
        read_only_fields = ['id', 'creado']

    def get_categoria_nombre(self, obj):
        if obj.categoria_ref:
            return obj.categoria_ref.nombre
        return obj.categoria or None

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value

    def validate_cantidad(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa")
        return value