from django.db import models

class Productos(models.Model):
    # Asumo que tienes un campo llamado 'nombre_producto'
    nombre_producto = models.CharField(max_length=255) 
    # ... otros campos ...
    
    def __str__(self):
        # ESTO ES LO QUE NECESITAS AGREGAR/CORREGIR
        return self.nombre_producto 
