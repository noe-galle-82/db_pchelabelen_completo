from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import parsers
from .models import Producto
from lotes.models import Lote
from lotes.serializers import LoteSerializer
from .serializers import ProductoSerializer
from .serializers import UserSerializer
from .serializers import EmpleadoCreateSerializer, EmpleadoSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import EmpleadoProfile
from .models import UserProfile
from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

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
    filterset_fields = ['categoria', 'categoria_ref', 'marca']
    search_fields = ['nombre', 'categoria', 'categoria_ref__nombre', 'marca__nombre_marca']
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


# Endpoint de salud para /api/ping/
@csrf_exempt
def ping(request):
    return JsonResponse({"status": "ok"}, status=200)

@action(detail=True, methods=['patch'])

# Endpoint para cambio de contraseña
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            return Response({'detail': 'Debe proporcionar old_password y new_password.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(old_password):
            return Response({'detail': 'La contraseña actual es incorrecta.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        # Resetear el flag must_change_password
        if hasattr(user, 'profile'):
            user.profile.must_change_password = False
            user.profile.save()
        return Response({'detail': 'Contraseña cambiada correctamente.'}, status=status.HTTP_200_OK)
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

    @action(detail=True, methods=['get'])
    def lotes(self, request, pk=None):
        """Historial de lotes del producto"""
        producto = self.get_object()
        lotes = Lote.objects.filter(producto=producto).order_by('-creado')
        serializer = LoteSerializer(lotes, many=True)
        return Response({
            'producto': producto.id,
            'total_lotes': lotes.count(),
            'data': serializer.data
        })

# ViewSet para operaciones CRUD completas de empleados
class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = EmpleadoProfile.objects.all()
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return EmpleadoSerializer
        return EmpleadoCreateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['user__username', 'user__email', 'numero_empleado']
    ordering_fields = ['user__username', 'numero_empleado']

class UserProfileDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        from .serializers import UserProfileSerializer
        try:
            profile = UserProfile.objects.get(user__id=pk)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'No existe el perfil.'}, status=status.HTTP_404_NOT_FOUND)