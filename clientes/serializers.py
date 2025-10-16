from rest_framework import serializers
from datetime import date
import re
from .models import Clientes
from django.contrib.auth.models import User


class ClienteSerializer(serializers.ModelSerializer):
    telefono = serializers.CharField(source='teléfono', allow_blank=True, allow_null=True, required=False)
    condicion_iva = serializers.ChoiceField(choices=Clientes.CONDICION_IVA, required=False, allow_null=True)

    class Meta:
        model = Clientes
        fields = [
            'id',
            'nombre_completo',
            'email',
            'telefono',
            'direccion',
            'dni',
            'fecha_nacimiento',
            'condicion_iva',
            'notas',
            'activo',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'email': { 'required': False, 'allow_null': True, 'allow_blank': False },
            'nombre_completo': { 'required': True },
            'dni': { 'required': False },
            'fecha_nacimiento': { 'required': False },
            'condicion_iva': { 'required': False },
            'notas': { 'required': False },
            'activo': { 'required': False },
        }

    def validate_email(self, value: str):
        if value in (None, ''):
            return None
        v = (value or '').strip().lower()
        return v

    def validate_telefono(self, value: str):
        if not value:
            return value
        # Acepta dígitos, espacios, +, -, paréntesis
        if not re.fullmatch(r"[\d\s\+\-\(\)]+", value):
            raise serializers.ValidationError("Formato de teléfono inválido")
        return value

    def validate_dni(self, value: str):
        if not value:
            return value
        # DNI básico: 7-10 dígitos
        if not re.fullmatch(r"\d{7,10}", value):
            raise serializers.ValidationError("DNI inválido (debe tener 7 a 10 dígitos)")
        return value

    def validate_fecha_nacimiento(self, value):
        if not value:
            return value
        if value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura")
        return value

    def validate_condicion_iva(self, value):
        if not value:
            return value
        # Normalizar a código en mayúsculas
        v = str(value).upper()
        codes = [c[0] for c in Clientes.CONDICION_IVA]
        if v not in codes:
            # Permitir pasar el label en vez del código
            labels = {label.upper(): code for code, label in Clientes.CONDICION_IVA}
            if v in labels:
                return labels[v]
            raise serializers.ValidationError("condicion_iva inválida")
        return v

    def validate(self, attrs):
        # Regla: exigir al menos uno entre email o dni
        email = attrs.get('email')
        dni = attrs.get('dni')
        if not email and not dni:
            raise serializers.ValidationError({'non_field_errors': ['Debe indicar email o DNI.']})
        return attrs

    def create(self, validated_data):
        telefono = validated_data.pop('teléfono', None)
        cliente = Clientes.objects.create(**validated_data)
        if telefono is not None:
            setattr(cliente, 'teléfono', telefono)
            cliente.save(update_fields=['teléfono'])
        return cliente

    def update(self, instance, validated_data):
        telefono = validated_data.pop('teléfono', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if telefono is not None:
            setattr(instance, 'teléfono', telefono)
        instance.save()
        return instance
