from django.db import models

class Marca(models.Model):
    nombre_marca = models.CharField(max_length=50, unique=True)
    notas = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.nombre_marca