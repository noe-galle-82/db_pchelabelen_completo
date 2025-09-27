from django.db import models

class Marca(models.Model):
    # El nombre de la marca (debe ser único para evitar duplicados)
    nombre_marca = models.CharField(max_length=50, unique=True) 

    class Meta:
        # Esto hace que el nombre en el Admin se vea bien
        verbose_name_plural = "Marcas"
        
    def __str__(self):
        # Muestra el nombre de la marca en el panel de administración
        return self.nombre_marca