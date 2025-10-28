from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Producto, EmpleadoProfile
from marcas.models import Marca
from marcas.serializers import MarcaSerializer
from productos.models import Categoria


# ------------------------------- # 
# Serializers de empleado #
# -------------------------------#
class EmpleadoProfileSerializer(serializers.ModelSerializer):
    dni = serializers.CharField(required=True)

    class Meta:
        model = EmpleadoProfile
        fields = [
            'role',
            'activo',
            'dni',
            'numero_empleado',
            'nombre',
            'apellido',
            'telefono',
            'contacto_emergencia',
            'numero_contacto_emergencia',
            'direccion',
            'fecha_nacimiento',
        ]

class UserEmpleadoSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    profile = EmpleadoProfileSerializer(source='empleadoprofile', required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "profile"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False}
        }

    def get_role(self, obj):
        return obj.groups.first().name if obj.groups.exists() else None

    def create(self, validated_data):
        profile_data = validated_data.pop('empleadoprofile')
        role = self.initial_data.get("role")

        # Generar username automáticamente: nombre + numero_empleado
        nombre = profile_data.get('nombre', 'user')
        numero_empleado = profile_data.get('numero_empleado', '')
        validated_data['username'] = f"{nombre}_{numero_empleado}"

        # Crear usuario
        user = User(**validated_data)

        # Asignar contraseña por defecto igual al DNI
        dni = profile_data.get('dni')
        if dni:
            user.set_password(str(dni))
        else:
            user.set_unusable_password()
        user.save()

        # Crear perfil de empleado
        EmpleadoProfile.objects.create(user=user, **profile_data)

        # Asignar rol/grupo
        if role:
            try:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('empleadoprofile', None)
        role = self.initial_data.get("role")
        password = validated_data.pop("password", None)

        # Actualizar campos de usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()

        # Actualizar perfil
        if profile_data:
            try:
                profile = EmpleadoProfile.objects.get(user=instance)
            except EmpleadoProfile.DoesNotExist:
                if not profile_data.get('dni'):
                    raise serializers.ValidationError({"dni": "El DNI es obligatorio para crear el perfil."})
                profile = EmpleadoProfile.objects.create(user=instance, **profile_data)

            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        # Actualizar rol
        if role:
            instance.groups.clear()
            try:
                group = Group.objects.get(name=role)
                instance.groups.add(group)
            except Group.DoesNotExist:
                pass

        return instance


# -------------------------------
# Serializers de categorías y productos
# -------------------------------
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
    marca_id = serializers.PrimaryKeyRelatedField(
        source='marca', queryset=Marca.objects.all(), allow_null=True, required=False
    )
    marca = MarcaSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'precio', 'cantidad',
            'categoria',
            'categoria_id',
            'categoria_nombre',
            'marca_id',
            'marca',
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
