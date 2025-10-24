from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import CompraConLotesSerializer

# Endpoint para registrar compra y lotes juntos
class RegistrarCompraView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = CompraConLotesSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			compra = serializer.save()
			return Response(CompraConLotesSerializer(compra).data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
