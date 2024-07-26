from rest_framework import viewsets ,permissions
from rest_framework.response import Response
from .models import Property
from .serializers import PropertySerializer

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]
 

    def list(self, request, *args, **kwargs):
        return Response({'detail': 'This endpoint is not available'})

# class PropertySearchView(APIView):
    