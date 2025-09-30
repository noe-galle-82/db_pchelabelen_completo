from django.db import models
from django.utils import timezone

# No necesitamos importar Cliente, Empleados o TipoPago.
# Usamos la notación de cadena ('app.Model') en los ForeignKey.

class Venta(models.Model):
    """
    Modelo que representa una Venta general en el sistema.
    Usa referencias de cadena para sus claves foráneas para evitar problemas 
    de carga de modelos (ValueError: related model has not been loaded yet).
    """
    
    # CLAVE: Referencia de cadena para Cliente
    cliente = models.ForeignKey('clientes.Clientes', on_delete=models.SET_NULL, null=True, blank=True, 
                                verbose_name="Cliente")
    
    # CLAVE: Referencia de cadena para Empleado
    empleado = models.ForeignKey('core.Empleados', on_delete=models.SET_NULL, null=True, 
                                 verbose_name="Empleado")
    
    # CLAVE: Referencia de cadena para TipoPago
    tipo_pago = models.ForeignKey('tipo_pago.TipoPago', on_delete=models.SET_NULL, null=True, 
                                  verbose_name="Tipo de Pago")
    
    fecha_venta = models.DateTimeField(default=timezone.now, 
                                       verbose_name="Fecha y Hora de Venta")
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                      verbose_name="Total de la Venta")
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']

    def __str__(self):
        return f"Venta #{self.pk} - Cliente: {self.cliente or 'N/A'}"

    def calcular_total(self):
        """Calcula y actualiza el campo total_venta sumando los subtotales de los detalles."""
        total = sum(detalle.subtotal for detalle in self.detalleventa_set.all())
        self.total_venta = total
        self.save()
