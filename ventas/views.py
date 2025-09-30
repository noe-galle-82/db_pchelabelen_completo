from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages

# Importamos solo el modelo de Venta (la app local)
from .models import Venta 
# 🚨 SOLUCIÓN: Solo importamos VentaForm aquí. 
# DetalleVentaFormSet se importa DENTRO de la función.
from .forms import VentaForm 
# Ya no necesitamos importar los modelos relacionados (Clientes, TipoPago, Empleado, Producto) 
# porque el ModelForm los maneja internamente usando referencias de cadena.

def registrar_venta(request):
    """
    Vista para manejar el registro de una nueva venta junto con sus detalles (productos).
    Utiliza un FormSet para los detalles de la venta.
    """
    # Importación movida dentro de la vista para evitar problemas de carga (ImportError/Circular Dependency)
    # Importamos aquí la función que necesitamos.
    from .forms import DetalleVentaFormSet 
    
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST, prefix='detalles')

        # Verificamos que tanto el formulario principal como el formset sean válidos
        if venta_form.is_valid() and formset.is_valid():
            try:
                # Usamos una transacción atómica para asegurar que ambas operaciones
                # (guardar Venta y guardar Detalles) tengan éxito o fallen juntas.
                with transaction.atomic():
                    # 1. Guardar la Venta principal
                    venta = venta_form.save(commit=False)
                    # Lógica de cálculo o asignación de otros campos (ej. total_venta) podría ir aquí
                    venta.save()

                    # 2. Guardar los Detalles de Venta
                    detalles = formset.save(commit=False)
                    for detalle in detalles:
                        detalle.venta = venta
                        # Lógica de actualización de stock o verificación de precio
                        detalle.save()

                messages.success(request, "¡Venta registrada exitosamente!")
                # Redirección a una URL de confirmación o resumen de ventas
                return redirect('home') 
                
            except Exception as e:
                # Si ocurre cualquier error inesperado, se muestra un mensaje de error
                # En un entorno real, la excepción 'e' debe ser manejada y logueada cuidadosamente.
                messages.error(request, f"Ocurrió un error al guardar la venta: {e}")
                # La transacción atómica revierte la base de datos a su estado anterior

        else:
            # Si hay errores de validación, se muestran los mensajes correspondientes
            # Usar print para debugging; messages para el usuario
            print(f"Errores en VentaForm: {venta_form.errors}")
            print(f"Errores en DetalleVentaFormSet: {formset.errors}")
            messages.error(request, "Por favor, corrige los errores en el formulario.")
            
    else:
        # Inicializar formularios para la solicitud GET
        venta_form = VentaForm()
        formset = DetalleVentaFormSet(prefix='detalles')

    context = {
        'venta_form': venta_form,
        'formset': formset,
        'titulo': 'Registrar Nueva Venta',
    }
    return render(request, 'ventas/registrar_venta.html', context)

# --- Vistas Adicionales ---

def venta_exitosa_placeholder(request):
    """
    Función placeholder simple requerida por ventas/urls.py
    """
    # Esta vista se reemplazará más adelante con una vista real
    # que muestre los detalles de la venta.
    return render(request, 'ventas/venta_exitosa.html', {'titulo': 'Venta Exitosa'})
