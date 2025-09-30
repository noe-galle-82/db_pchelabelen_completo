from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.contrib import messages
# Importaciones de modelos. Ajustamos DetalleCompra.
from .models import Compras, Proveedores, TipoPago
from detalles_compra.models import DetalleCompra # <--- CORREGIDO: Importamos desde la app correcta
from .forms import ComprasForm, DetalleCompraForm
from productos.models import Productos # Asumo que Productos existe
# from django.contrib.auth.decorators import login_required # <--- YA NO NECESARIO

# Vistas de Compras. Eliminamos el decorador @login_required para hacerlas públicas.

def listar_compras(request):
    """Muestra la lista de todas las compras (Implementación pendiente)."""
    # Esta vista necesita ser completada con la lógica de listado.
    # Por ahora, solo cargaremos la plantilla.
    compras = Compras.objects.all().order_by('-fecha_compra')
    return render(request, 'compras/listar_compras.html', {'compras': compras})


def registrar_compra(request):
    """Maneja el formulario de registro de una nueva compra y sus detalles."""
    # Nota: Si DetalleCompraForm no existe, DetalleCompraFormSet fallará.
    DetalleCompraFormSet = inlineformset_factory(
        Compras, 
        DetalleCompra, 
        form=DetalleCompraForm, 
        extra=1, 
        can_delete=False
    )
    
    if request.method == 'POST':
        compra_form = ComprasForm(request.POST)
        
        if compra_form.is_valid():
            compra = compra_form.save(commit=False)
            
            # Asignar el empleado (Se asume que el usuario autenticado es el empleado,
            # pero como la vista es pública, esta lógica DEBERÍA REVISARSE).
            # Para fines de prueba, lo dejaremos temporalmente sin asignar.
            # compra.id_empleado = request.user.empleado # <--- COMENTADO POR SEGURIDAD PÚBLICA
            
            compra.save()
            
            formset = DetalleCompraFormSet(request.POST, instance=compra)
            if formset.is_valid():
                formset.save()
                messages.success(request, '¡La compra y sus detalles se han registrado correctamente!')
                return redirect('compras:listar_compras')
            else:
                messages.error(request, 'Hubo un error en los detalles de la compra.')
                compra.delete() # Revertir la compra principal si fallan los detalles
        else:
            messages.error(request, 'Hubo un error en los datos principales de la compra.')

    else:
        compra_form = ComprasForm()
        formset = DetalleCompraFormSet()

    template_name = 'compras/registrar_compra.html'
    context = {
        'compra_form': compra_form, 
        'formset': formset
    }
    return render(request, template_name, context)

# ... (otras vistas de Compras si las tienes)
