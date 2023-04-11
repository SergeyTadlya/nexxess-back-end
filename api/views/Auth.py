from rest_framework import generics
from api.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.forms import model_to_dict


class UserAPICreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ['id', 'username', 'email']


class UserAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_fields = ['id']

    def patch(self, request, pk):
        user = User.objects.get(id=pk)
        if 'username' in request.data:
            user.username = request.data['username']
        if 'email' in request.data:
            user.email = request.data['email']
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'password' in request.data:
            user.password = request.data['password']
        if 'is_staff' in request.data:
            user.is_staff = request.data['is_staff']
        user.save()
        return Response(model_to_dict(user))