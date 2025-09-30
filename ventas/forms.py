from django import forms
from django.forms.models import inlineformset_factory
from django.apps import apps
# Asegúrate de que el modelo Venta esté en esta app o importalo correctamente
from .models import Venta 
# ELIMINADA: from detalles_venta.models import DetalleVenta (Usamos carga diferida)

# La técnica apps.get_model se usa para evitar errores de dependencia circular.

class VentaForm(forms.ModelForm):
    # Campo para Cliente (App: clientes, Modelo: Clientes)
    cliente = forms.ModelChoiceField(
        queryset=apps.get_model('clientes', 'Clientes').objects.all(),
        label="Cliente",
        required=True
    )

    # Campo para Empleado (App: core, Modelo: EmpleadoProfile)
    empleado = forms.ModelChoiceField(
        queryset=apps.get_model('core', 'EmpleadoProfile').objects.all(),
        label="Empleado",
        required=True
    )

    # Campo para Tipo de Pago (App: tipo_pago, Modelo: TipoPago)
    tipo_pago = forms.ModelChoiceField(
        queryset=apps.get_model('tipo_pago', 'TipoPago').objects.all(),
        label="Tipo de Pago",
        required=True
    )