from django.db import models

class Compras(models.Model):
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateField(auto_now_add=True)
    # Referencias a otras apps
    id_proveedor = models.ForeignKey('proveedores.Proveedores', on_delete=models.CASCADE)
    id_usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'Compra #{self.id}'
