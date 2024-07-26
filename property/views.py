from rest_framework import viewsets ,permissions
from rest_framework.response import Response
from .models import Property
from .serializers import PropertySerializer
from .permissions import IsPropertyOwner
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        else:
            return [IsPropertyOwner()]
 

    def list(self, request, *args, **kwargs):
        return Response({'detail': 'This endpoint is not available'})
# Choosing fuzzy logic for search feature in app
# class PropertySearchView(APIView):
    