from rest_framework import viewsets, permissions, filters
from .models import Lote
from .serializers import LoteSerializer

class LoteViewSet(viewsets.ModelViewSet):
	queryset = Lote.objects.select_related('producto').all()
	serializer_class = LoteSerializer
	permission_classes = [permissions.IsAuthenticated]
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ['numero_lote', 'producto__nombre', 'proveedor']
	ordering_fields = ['fecha_compra', 'fecha_vencimiento', 'cantidad_inicial', 'cantidad_disponible']
	ordering = ['-fecha_compra']

	def get_queryset(self):
		qs = super().get_queryset()
		producto_id = self.request.query_params.get('producto')
		if producto_id:
			qs = qs.filter(producto_id=producto_id)
		return qs
