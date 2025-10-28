from django.urls import path, include
from .views import ping, UserViewSet, ProductoViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'empleados', UserViewSet, basename='empleados')
router.register(r'productos', ProductoViewSet, basename='productos')

urlpatterns = [
    path('api/ping/', ping),
    path('api/', include(router.urls)),
]
