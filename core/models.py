from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

# ==========================================================
# 1. PERFIL DE EMPLEADO
# ==========================================================
class EmpleadoProfile(models.Model):
    # Enlazamos al usuario de Django (tabla auth_user)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario del Sistema')
    # Campos que vienen de la tabla Usuarios y Tipo_usuario
    nombre_tipo_usuario = models.CharField(max_length=50, blank=True, verbose_name='Rol (Cajero/Repositor)') # Usado para referencia rápida
    
    # Nuevo campo para identificar al empleado en la empresa
    numero_empleado = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    # Campo de la tabla Usuarios que usaríamos del modelo de Django: email_usuario -> user.email
    # Campo de la tabla Usuarios que usaríamos del modelo de Django: password_hash -> user.password

    def __str__(self):
        return f"Empleado: {self.user.username} ({self.nombre_tipo_usuario})"

# ==========================================================
# 2. CATEGORÍAS DE PRODUCTOS
# ==========================================================

class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=0)
    # Campo legacy (texto) - se eliminará tras migrar datos a categoria_ref
    categoria = models.CharField(max_length=80, blank=True)
    # Nuevo FK a Categoria (app productos)
    categoria_ref = models.ForeignKey(
        'productos.Categoria', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='productos'
    )
    # Nueva relación a Marca (app marcas)
    marca = models.ForeignKey(
        'marcas.Marca', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='productos'
    )
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)  # opcional
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

# SEÑALES PARA ELIMINAR IMÁGENES AUTOMÁTICAMENTE

@receiver(post_delete, sender=Producto)
def eliminar_imagen_producto(sender, instance, **kwargs):
    """
    Elimina la imagen del disco cuando se elimina un producto
    """
    if instance.imagen:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)

@receiver(pre_save, sender=Producto)
def eliminar_imagen_anterior(sender, instance, **kwargs):
    """
    Elimina la imagen anterior cuando se actualiza con una nueva imagen
    """
    if not instance.pk:
        return False
    
    try:
        old_file = Producto.objects.get(pk=instance.pk).imagen
    except Producto.DoesNotExist:
        return False
    
    new_file = instance.imagen
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)

# ==========================================================
# 3. VENTAS
# ==========================================================