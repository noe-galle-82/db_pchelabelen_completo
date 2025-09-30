from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. Protección del Administrador
    path('admin/', admin.site.urls), 
    
    # 2. Rutas de Autenticación de Django
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 3. Rutas de la aplicación 'core'
    path('', include('core.urls')), 
    
    # 4. Rutas de tus aplicaciones de negocio (TODAS LAS APPS)
    path('compras/', include('compras.urls')),
    path('clientes/', include('clientes.urls')),
    # --- ¡Línea Corregida! ---
    path('detalles_compra/', include('detalles_compra.urls')), 
    # -------------------------
    path('detalles_venta/', include('detalles_venta.urls')),
    path('lotes/', include('lotes.urls')),
    path('marcas/', include('marcas.urls')),
    path('movimientos_caja/', include('movimientos_caja.urls')),
    path('productos/', include('productos.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('tipo_movimientos/', include('tipo_movimientos.urls')),
    path('tipo_pago/', include('tipo_pago.urls')),
    path('ventas/', include('ventas.urls')),
    # Aquí es donde deberemos incluir 'empleados/' cuando trabajemos en esa rama.
]