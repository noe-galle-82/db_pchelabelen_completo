from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Clientes
from .serializers import ClienteSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class ClienteViewSet(viewsets.ModelViewSet):
	queryset = Clientes.objects.all().order_by('nombre_completo')
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
