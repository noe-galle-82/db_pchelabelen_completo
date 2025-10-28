from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import parsers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import EmpleadoProfile, Producto
from lotes.models import Lote
from lotes.serializers import LoteSerializer
from .serializers import ProductoSerializer, UserEmpleadoSerializer


# ===============================
# Endpoints generales
# ===============================

# Obtener info del usuario logueado
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


# Obtener todos los usuarios
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


# ===============================
# Endpoints para Empleados
# ===============================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def empleados_list(request):
    """Devuelve todos los empleados activos"""
    empleados = EmpleadoProfile.objects.filter(activo=True).select_related("user")
    data = [{
        "id": e.id,
        "nombre": e.user.first_name,
        "apellido": e.user.last_name,
        "email": e.user.email,
        "numero_empleado": e.numero_empleado,
        "role": e.nombre_tipo_usuario,
        "activo": e.activo,
    } for e in empleados]
    return Response(data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def empleados_update(request, pk):
    """Actualizar datos del empleado"""
    try:
        empleado = EmpleadoProfile.objects.get(pk=pk)
    except EmpleadoProfile.DoesNotExist:
        return Response({"detail": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    user = empleado.user

    # Solo actualizar campos permitidos
    user.first_name = data.get("nombre", user.first_name)
    user.last_name = data.get("apellido", user.last_name)
    user.email = data.get("email", user.email)
    empleado.numero_empleado = data.get("numero_empleado", empleado.numero_empleado)
    empleado.nombre_tipo_usuario = data.get("role", empleado.nombre_tipo_usuario)
    empleado.activo = data.get("activo", empleado.activo)

    user.save()
    empleado.save()

    return Response({"detail": "Empleado actualizado correctamente"})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def empleados_inactivar(request, pk):
    """Marca un empleado como inactivo (soft delete)"""
    try:
        empleado = EmpleadoProfile.objects.get(pk=pk)
    except EmpleadoProfile.DoesNotExist:
        return Response({"detail": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    empleado.activo = False
    empleado.save()
    return Response({"detail": "Empleado inactivado correctamente"})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def empleados_reactivar(request, pk):
    """Reactivar empleado previamente inactivado"""
    try:
        empleado = EmpleadoProfile.objects.get(pk=pk)
    except EmpleadoProfile.DoesNotExist:
        return Response({"detail": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    empleado.activo = True
    empleado.save()
    return Response({"detail": "Empleado reactivado correctamente"})


# ===============================
# ViewSets
# ===============================

# ViewSet para operaciones CRUD de usuarios
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserEmpleadoSerializer
    permission_classes = [IsAuthenticated]


# ViewSet para operaciones CRUD de productos
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria', 'categoria_ref', 'marca']
    search_fields = ['nombre', 'categoria', 'categoria_ref__nombre', 'marca__nombre_marca']
    ordering_fields = ['nombre', 'precio', 'cantidad', 'creado']
    ordering = ['-creado']
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def create(self, request, *args, **kwargs):
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
        instance = self.get_object()
        producto_nombre = instance.nombre
        instance.delete()
        return Response({
            'message': f'Producto "{producto_nombre}" eliminado exitosamente'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def categorias(self, request):
        categorias = Producto.objects.values_list('categoria', flat=True).distinct()
        categorias_filtradas = [cat for cat in categorias if cat]
        return Response({'categorias': categorias_filtradas})

    @action(detail=False, methods=['get'])
    def productos_bajo_stock(self, request):
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
        producto = self.get_object()
        nueva_cantidad = request.data.get('cantidad')

        if nueva_cantidad is None:
            return Response({'message': 'Debe proporcionar la nueva cantidad'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'message': f'Error en la cantidad: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def lotes(self, request, pk=None):
        producto = self.get_object()
        lotes = Lote.objects.filter(producto=producto).order_by('-creado')
        serializer = LoteSerializer(lotes, many=True)
        return Response({
            'producto': producto.id,
            'total_lotes': lotes.count(),
            'data': serializer.data
        })


# ===============================
# Endpoint de salud
# ===============================

@csrf_exempt
def ping(request):
    return JsonResponse({"status": "ok"}, status=200)
