from django import forms 
from django.shortcuts import render, redirect, get_object_or_404 
from django.forms import inlineformset_factory
from django.db import transaction
from django.contrib import messages
from django.db.models import F # Importar F para posibles actualizaciones optimizadas

# Importamos los modelos necesarios
from .models import Ventas 
# Asumiendo que existe una app para los detalles de venta
from detalles_venta.models import DetalleVenta 
from lotes.models import Lotes
from productos.models import Productos 
# Importa Clientes
# from clientes.models import Clientes 

# ==============================================================================
# 1. Definición de Formularios
# ==============================================================================

class VentasForm(forms.ModelForm):
    """
    Formulario principal para el modelo Ventas.
    """
    class Meta:
        model = Ventas
        # Se asume que Ventas usa id_cliente, id_empleado y id_tipo_pago
        fields = ['id_cliente', 'id_empleado', 'id_tipo_pago'] 

class DetalleVentaForm(forms.ModelForm):
    """
    Formulario para cada línea de DetalleVenta.
    """
    class Meta:
        model = DetalleVenta
        # Se asume que DetalleVenta usa id_producto, cantidad y precio_venta
        fields = ['id_producto', 'cantidad', 'precio_venta']
        
# Creamos un Formset para manejar múltiples DetalleVenta anidados bajo una Venta.
DetalleVentaFormSet = inlineformset_factory(
    Ventas, 
    DetalleVenta, 
    form=DetalleVentaForm, 
    extra=1, 
    can_delete=True
)

# ==============================================================================
# 2. Funcionalidad clave: Consumir Lote y Actualizar Stock (Lógica Inversa FIFO)
# ==============================================================================
def consumir_lote_y_actualizar_stock(detalle_venta_instancia):
    """
    Implementa la lógica FIFO: busca los lotes más antiguos (por PK o fecha), 
    consume el stock de ellos, y actualiza el stock general del producto.
    
    Argumento:
        detalle_venta_instancia (DetalleVenta): Instancia del detalle recién guardado.
    """
    producto = detalle_venta_instancia.id_producto
    cantidad_a_vender = detalle_venta_instancia.cantidad
    cantidad_restante = cantidad_a_vender
    
    # 1. Validar que el producto tenga suficiente stock total
    stock_total_actual = producto.stock or 0
    if stock_total_actual < cantidad_a_vender:
        # Forzamos una excepción de stock insuficiente
        raise Exception(f"Stock insuficiente para el producto {producto.nombre_producto} (ID: {producto.pk}). Stock disponible: {stock_total_actual}")
        
    # 2. Búsqueda y consumo de Lotes (FIFO: Ordenar por PK o fecha de creación ascendente)
    # Solo consideramos lotes con stock > 0
    lotes_disponibles = Lotes.objects.filter(
        id_producto=producto,
        stock__gt=0
    ).order_by('pk') # El PK es generalmente un buen proxy para la antigüedad (FIFO)
    
    for lote in lotes_disponibles:
        if cantidad_restante <= 0:
            break
            
        # Determinar cuánto stock se toma de este lote
        cantidad_a_consumir = min(cantidad_restante, lote.stock)
        
        # 3. Disminuir el stock del lote y guardar
        lote.stock = F('stock') - cantidad_a_consumir # Usamos F() para evitar condiciones de carrera (opcional, pero buena práctica)
        lote.save(update_fields=['stock'])
        
        # 4. Actualizar la cantidad restante a vender
        cantidad_restante -= cantidad_a_consumir
        
    # 5. Comprobación de seguridad (solo si la lógica de lotes falló a pesar del stock total)
    if cantidad_restante > 0:
         # Esto no debería ocurrir si la validación inicial pasó y los lotes están correctos
         raise Exception(f"Error de inventario: No se pudo consumir toda la cantidad ({cantidad_restante} restante) de los lotes.")
         
    # 6. Actualizar el stock general del Producto (Disminución total)
    # Usamos F() para realizar la operación a nivel de base de datos de manera segura
    producto.stock = F('stock') - cantidad_a_vender
    producto.save(update_fields=['stock'])
    
    # Recargar el producto (si es necesario para otras operaciones en el mismo request, aunque no aquí)
    # producto.refresh_from_db() 


# ==============================================================================
# 3. Vistas
# ==============================================================================
def registrar_venta(request):
    """
    Vista principal para registrar una nueva venta, sus detalles y actualizar el inventario.
    """
    template_name = 'ventas/registrar_venta.html' 
    
    # POST: Manejo del Formulario
    if request.method == 'POST':
        # Nota: El formulario principal fue renombrado a 'VentasForm'
        venta_form = VentasForm(request.POST) 
        formset = DetalleVentaFormSet(request.POST, instance=Ventas())
        
        if venta_form.is_valid() and formset.is_valid():
            
            try:
                # Transacción atómica: si algo falla (ej. stock), se revierte todo
                with transaction.atomic():
                    venta_instancia = venta_form.save(commit=False)
                    total_venta = 0 
                    detalle_instancias = formset.save(commit=False)
                    
                    # 1. Pre-cálculo de Monto Total y Subtotales de Detalle
                    for detalle in detalle_instancias:
                        # Solo procesar si el detalle no está marcado para eliminación
                        if not detalle.DELETE and detalle.cantidad and detalle.precio_venta:
                            # Subtotal es cantidad * precio_venta
                            monto_total_detalle = detalle.cantidad * detalle.precio_venta 
                            detalle.subtotal = monto_total_detalle
                            total_venta += monto_total_detalle
                        
                    # 2. Guardar la Venta Principal
                    venta_instancia.monto_total = total_venta
                    venta_instancia.save() 
                    
                    # 3. Guardar Detalles y Consumir Stock
                    for detalle in detalle_instancias:
                        if not detalle.DELETE:
                            detalle.id_venta = venta_instancia
                            detalle.save() 
                            
                            # 4. Consumir Lote y Actualizar Stock (CRÍTICO)
                            if detalle.cantidad > 0:
                                consumir_lote_y_actualizar_stock(detalle)
                        # Nota: Los detalles eliminados son manejados por formset.save_m2m() si aplica, pero aquí lo omitimos
                        # ya que estamos en commit=False. No obstante, si se borra un form, no entra en detalle_instancias.

                    messages.success(request, f"La venta (Total: {total_venta}) fue registrada exitosamente y el inventario fue actualizado.")
                    # Redirección a la ruta de éxito
                    return redirect('venta_exitosa') 
                
            except Exception as e:
                # Manejamos la excepción de stock u otra generada en la transacción
                messages.error(request, f"Ocurrió un error al guardar la venta: {e}. La transacción fue revertida.")
                # Si falla, aseguramos que los formularios vuelvan a tener los datos POST
                compra_form = VentasForm(request.POST)
                formset = DetalleVentaFormSet(request.POST, instance=Ventas())
                
        else:
            messages.error(request, "Por favor, corrige los errores en los formularios.")
            # Si falla la validación, los formularios ya están cargados con request.POST
            compra_form = VentasForm(request.POST)
            formset = DetalleVentaFormSet(request.POST, instance=Ventas())
            
    # GET: Inicialización de Formularios
    else:
        compra_form = VentasForm()
        formset = DetalleVentaFormSet(instance=Ventas()) 

    # Contexto y Renderizado
    context = {
        'venta_form': compra_form,
        'formset': formset,
    }
    return render(request, template_name, context)

def venta_exitosa_placeholder(request):
    """
    Vista placeholder para mostrar un mensaje de éxito después de registrar una venta.
    """
    # TODO: Crear el template 'ventas/venta_exitosa.html'
    return render(request, 'ventas/venta_exitosa.html', {'message': 'La venta se registró exitosamente y el inventario fue actualizado.'})
