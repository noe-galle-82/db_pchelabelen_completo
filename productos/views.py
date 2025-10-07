from rest_framework import viewsets, permissions
from .models import Categoria
from .serializers import CategoriaSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
	queryset = Categoria.objects.all().order_by('nombre')
	serializer_class = CategoriaSerializer
	permission_classes = [permissions.IsAuthenticated]
