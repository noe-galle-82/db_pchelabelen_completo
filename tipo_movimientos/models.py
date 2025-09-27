from django.db import models

class TipoMovimiento(models.Model):
    # La clave primaria ya está definida implícitamente por Django (id)
    nombre_tipo_movimiento = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Tipo de Movimiento"
        verbose_name_plural = "Tipos de Movimiento"

    def __str__(self):
        return self.nombre_tipo_movimiento