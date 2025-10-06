from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import parsers
from .models import Producto

from .serializers import ProductoSerializer
from .serializers import UserSerializer

# Create your views here.

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    groups = [g.name for g in user.groups.all()]
    return Response({
        "id": user.id,
        "username": user.username,
        "role": groups[0] if groups else None,
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.all()
    users_data = []
    
    for user in users:
        groups = [g.name for g in user.groups.all()]
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": groups[0] if groups else None,
        })
    
    return Response(users_data)


# ViewSet para operaciones CRUD completas de usuarios
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


# ViewSet para operaciones CRUD completas de productos
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria']
    search_fields = ['nombre', 'categoria']
    ordering_fields = ['nombre', 'precio', 'cantidad', 'creado']
    ordering = ['-creado']  # Por defecto ordenar por más reciente
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


    def create(self, request, *args, **kwargs):
        """Crear un nuevo producto"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Producto creado exitosamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Error al crear el producto',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Actualizar producto completo"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Producto actualizado exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Error al actualizar el producto',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        """Eliminar producto"""
        instance = self.get_object()
        producto_nombre = instance.nombre
        instance.delete()
        return Response({
            'message': f'Producto "{producto_nombre}" eliminado exitosamente'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def categorias(self, request):
        """Obtener todas las categorías únicas"""
        categorias = Producto.objects.values_list('categoria', flat=True).distinct()
        categorias_filtradas = [cat for cat in categorias if cat]  # Excluir vacías
        return Response({
            'categorias': categorias_filtradas
        })

    @action(detail=False, methods=['get'])
    def productos_bajo_stock(self, request):
        """Productos con cantidad menor a un umbral"""
        umbral = request.query_params.get('umbral', 10)
        try:
            umbral = int(umbral)
        except ValueError:
            umbral = 10
        
        productos = Producto.objects.filter(cantidad__lt=umbral).order_by('cantidad')
        serializer = self.get_serializer(productos, many=True)
        return Response({
            'message': f'Productos con menos de {umbral} unidades',
            'data': serializer.data
        })

    @action(detail=True, methods=['patch'])
    def actualizar_stock(self, request, pk=None):
        """Actualizar solo el stock de un producto"""
        producto = self.get_object()
        nueva_cantidad = request.data.get('cantidad')
        
        if nueva_cantidad is None:
            return Response({
                'message': 'Debe proporcionar la nueva cantidad'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            nueva_cantidad = int(nueva_cantidad)
            if nueva_cantidad < 0:
                raise ValueError("La cantidad no puede ser negativa")
            
            producto.cantidad = nueva_cantidad
            producto.save()
            
            serializer = self.get_serializer(producto)
            return Response({
                'message': f'Stock actualizado a {nueva_cantidad} unidades',
                'data': serializer.data
            })
        except ValueError as e:
            return Response({
                'message': f'Error en la cantidad: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
