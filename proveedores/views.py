from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Proveedores
from .serializers import ProveedorSerializer

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedores.objects.all().order_by('nombre')
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "No se puede eliminar porque tiene lotes asociados."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
