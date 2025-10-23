from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import me, get_users, UserViewSet, ProductoViewSet, EmpleadoViewSet
from productos.views import CategoriaViewSet
from lotes.views import LoteViewSet
from proveedores.views import ProveedorViewSet
from clientes.views import ClienteViewSet
from marcas.views import MarcaViewSet
from movimientos_caja.views import CajaViewSet, MovimientoDeCajaViewSet
from ventas.views import VentaViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'lotes', LoteViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'caja', CajaViewSet, basename='caja')
router.register(r'caja-movimientos', MovimientoDeCajaViewSet, basename='caja-movimientos')
router.register(r'ventas', VentaViewSet, basename='ventas')
router.register(r'empleados', EmpleadoViewSet, basename='empleados')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path("api/", include(router.urls)),
    path("api/me/", me, name="me"),
    path("api/users/", get_users, name="get_users"),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
