from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Clientes
from .serializers import ClienteSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class ClienteViewSet(viewsets.ModelViewSet):
	queryset = Clientes.objects.all().order_by('apellido', 'nombre')
	serializer_class = ClienteSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ['email', 'dni', 'activo', 'condicion_iva']
	search_fields = ['nombre_completo', 'email', 'dni']
	ordering_fields = ['nombre_completo', 'email', 'dni']

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def update(self, request, *args, **kwargs):
		instance = self.get_object()
		if instance.id == 1:
			return Response({"detail": "No se puede modificar el cliente Venta Rápida."}, status=status.HTTP_403_FORBIDDEN)
		return super().update(request, *args, **kwargs)

	def partial_update(self, request, *args, **kwargs):
		instance = self.get_object()
		if instance.id == 1:
			return Response({"detail": "No se puede modificar el cliente Venta Rápida."}, status=status.HTTP_403_FORBIDDEN)
		return super().partial_update(request, *args, **kwargs)

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		if instance.id == 1:
			return Response({"detail": "No se puede eliminar el cliente Venta Rápida."}, status=status.HTTP_403_FORBIDDEN)
		return super().destroy(request, *args, **kwargs)

	@action(detail=False, methods=['get'], url_path='unique-check')
	def unique_check(self, request):
		"""Prevalida duplicados de email y DNI para evitar 400 en el submit.

		Query params:
		- email: opcional
		- dni: opcional

		Respuesta: { email: {exists: bool}, dni: {exists: bool} }
		"""
		email = (request.query_params.get('email') or '').strip().lower()
		dni = (request.query_params.get('dni') or '').strip()
		resp = {"email": {"exists": False}, "dni": {"exists": False}}
		qs = self.get_queryset()
		if email:
			resp["email"]["exists"] = qs.filter(email=email).exists()
		if dni:
			resp["dni"]["exists"] = qs.filter(dni=dni).exists()
		return Response(resp)

	@action(detail=False, methods=['get'])
	def catalogos(self, request):
		"""Devuelve los códigos/labels de condición IVA para poblar selects en el front."""
		choices = [
			{"code": code, "label": label}
			for code, label in Clientes.CONDICION_IVA
		]
		return Response({"condicion_iva": choices})
