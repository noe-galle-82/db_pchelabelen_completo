from django.db import models

class TipoPago(models.Model):
    # La clave primaria ya está definida implícitamente por Django (id)
    nombre_tipo_pago = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Tipo de Pago"
        verbose_name_plural = "Tipos de Pago"

    def __str__(self):
        return self.nombre_tipo_pago