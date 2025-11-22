from .models import UserProfile
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Producto, EmpleadoProfile, UserProfile
from marcas.models import Marca
from marcas.serializers import MarcaSerializer
from productos.models import Categoria
from django.db import transaction
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
import random
import string
import random
import string



# Serializer para exponer must_change_password y datos básicos del usuario
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    role = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'role', 'must_change_password']

    def get_role(self, obj):
        groups = obj.user.groups.all()
        return groups[0].name if groups else None
    
class EmpleadoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = EmpleadoProfile
        fields = [
            'id', 'user_id', 'username', 'email', 'role',
            'nombre', 'apellido', 'dni', 'telefono', 'contacto_emergencia',
            'numero_contacto_emergencia', 'direccion', 'fecha_nacimiento',
            'nombre_tipo_usuario', 'activo'
        ]

    def get_role(self, obj):
        groups = obj.user.groups.all()
        return groups[0].name if groups else None


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
    marca_id = serializers.PrimaryKeyRelatedField(
        source='marca', queryset=Marca.objects.all(), allow_null=True, required=False
    )
    marca = MarcaSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'precio', 'cantidad',
            'categoria',          # legacy texto (temporal)
            'categoria_id',       # FK writable
            'categoria_nombre',   # derivado
            'marca_id',           # FK writable
            'marca',              # nested read-only
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

class EmpleadoCreateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        email = validated_data.get('email', instance.email)
        role = validated_data.get('role', None)
        # Actualizar email en User si cambió
        if email != instance.user.email:
            instance.user.email = email
            instance.user.save(update_fields=['email'])
        # Actualizar grupo/rol si cambió
        if role:
            instance.user.groups.clear()
            group, _ = Group.objects.get_or_create(name=role)
            instance.user.groups.add(group)
        # Actualizar el resto de los campos (excepto email y role)
        for attr, value in validated_data.items():
            if attr not in ['email', 'role']:
                setattr(instance, attr, value)
        instance.save()
        return instance
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(write_only=True)

    class Meta:
        model = EmpleadoProfile
        fields = [
            'id',
            'username', 'email', 'password', 'role',
            'nombre', 'apellido', 'dni', 'telefono', 'contacto_emergencia',
            'numero_contacto_emergencia', 'direccion', 'fecha_nacimiento',
            'nombre_tipo_usuario', 'activo'
        ]
        extra_kwargs = {
            'nombre': {'required': True},
            'apellido': {'required': True},
            'dni': {'required': True},
            'email': {'required': True},
        }

    def validate_email(self, value):
        if EmpleadoProfile.objects.filter(email=value).exists() or User.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está registrado para otro empleado o usuario.")
        return value

    def validate_dni(self, value):
        qs = EmpleadoProfile.objects.filter(dni=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("El DNI ya está registrado para otro empleado.")
        return value

    def create(self, validated_data):
        nombre = validated_data.pop('nombre', None)
        apellido = validated_data.pop('apellido', None)
        email = validated_data.pop('email')
        password = validated_data.pop('password', None)
        role = validated_data.pop('role')
        # Generar username automáticamente
        base_username = f"{nombre}.{apellido}".lower().replace(' ', '')
        username = base_username
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{i}"
            i += 1
        if not password:
            password = self.generate_password()
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            # Forzar must_change_password en el perfil del usuario
            if hasattr(user, 'profile'):
                user.profile.must_change_password = True
                user.profile.save()
            if role:
                group, _ = Group.objects.get_or_create(name=role)
                user.groups.add(group)
            empleado = EmpleadoProfile.objects.create(user=user, email=email, nombre=nombre, apellido=apellido, **validated_data)
        # Enviar email con credenciales
        subject = 'Bienvenido a PCHELABELEN - Credenciales de acceso'
        message = f"Hola {nombre},\n\nTu usuario ha sido creado en el sistema.\n\nUsuario: {username}\nContraseña temporal: {password}\n\nPor seguridad, deberás cambiar la contraseña al iniciar sesión por primera vez.\n\nSaludos."
        send_mail(subject, message, None, [email], fail_silently=True)
        return empleado

    def generate_password(self, length=10):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
