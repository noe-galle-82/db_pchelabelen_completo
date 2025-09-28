from django.contrib.auth.models import User, Group
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


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