from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

# ==========================================================
# 1. PERFIL DE EMPLEADO
# ==========================================================
class EmpleadoProfile(models.Model):
    ROLE_CHOICES = [
        ('gerente', 'Gerente'),
        ('empleado', 'Empleado'),
        ('cajero', 'Cajero'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario del Sistema')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='Rol del empleado')
    numero_empleado = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    contacto_emergencia = models.CharField(max_length=100, blank=True, null=True)
    numero_contacto_emergencia = models.CharField(max_length=30, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.role})"

# ==========================================================
# 2. CATEGORÍAS DE PRODUCTOS
# ==========================================================

class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=80, blank=True)
    categoria_ref = models.ForeignKey(
        'productos.Categoria', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='productos'
    )
    marca = models.ForeignKey(
        'marcas.Marca', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='productos'
    )
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)  # opcional
    creado = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

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