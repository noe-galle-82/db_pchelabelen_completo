from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    # 1. Rutas de Django Admin
    path('admin/', admin.site.urls),
    
    # 2. Rutas de Autenticación de Django (login, logout, password reset, etc.)
    # Esta línea es CLAVE para que LOGIN_URL funcione.
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 3. Rutas de tu aplicación de Compras
    path('compras/', include('compras.urls')), 
    
    # Aquí incluirías las rutas de todas tus otras aplicaciones
    # path('productos/', include('productos.urls')),
    # path('ventas/', include('ventas.urls')),
    # path('clientes/', include('clientes.urls')), # <--- La próxima tarea
]