from django import forms
from compras.models import Compras # Asume que Compras está en compras/models.py
from detalles_compra.models import DetalleCompra # Asume que DetalleCompra está en detalles_compra/models.py
from proveedores.models import Proveedores
from tipo_pago.models import TipoPago
from productos.models import Productos

# --- Formularios de Compras ---

class ComprasForm(forms.ModelForm):
    """
    Formulario principal para registrar una Compra.
    Utiliza un ModelForm para mapear los campos del modelo Compras.
    """
    class Meta:
        model = Compras
        fields = ['id_proveedor', 'id_empleado', 'id_tipo_pago']
        widgets = {
            'id_proveedor': forms.Select(attrs={'class': 'form-control'}),
            # El campo de empleado lo ocultamos o lo gestionaremos automáticamente.
            # Por ahora, se deja visible para desarrollo, pero se asigna en la vista.
            'id_empleado': forms.Select(attrs={'class': 'form-control'}), 
            'id_tipo_pago': forms.Select(attrs={'class': 'form-control'}),
        }
    
    # Este constructor es solo para hacer los campos 'required=False'
    # Temporalmente para pruebas, si tienes problemas con valores NULL.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: ajustar queryset si es necesario
        self.fields['id_proveedor'].queryset = Proveedores.objects.all()
        self.fields['id_tipo_pago'].queryset = TipoPago.objects.all()
        # Nota: El queryset para id_empleado dependerá de la app empleados.


class DetalleCompraForm(forms.ModelForm):
    """
    Formulario para la línea de detalle de la compra (producto, cantidad, costo).
    """
    class Meta:
        model = DetalleCompra
        fields = ['id_producto', 'cantidad', 'costo_unitario']
        widgets = {
            'id_producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_producto'].queryset = Productos.objects.filter(activo=True)
