from rest_framework import generics
from api.serializers import UserSerializer
from telegram_bot.models import User
from rest_framework.response import Response
from django.forms import model_to_dict


class UserAPICreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ['id', 'email']

    def post(self, email=None, name=None, telegram_id=None, first_name=None, last_name=None, is_staff=False, password=None):
        user = User()

        user.email = email if email is not None else None
        user.name = name if name is not None else None
        user.telegram_id = telegram_id if telegram_id is not None else None
        user.first_name = first_name if first_name is not None else None
        user.last_name = last_name if last_name is not None else None
        user.is_staff = is_staff if is_staff is not None else None
        user.email = email if email is not None else None
        if password is not None:
            user.set_password(password)
        user.save()

        return Response(model_to_dict(user))


class UserAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_fields = ['id']

    def patch(self, request, pk):
        user = User.objects.get(id=pk)
        print(request.data)
        if 'email' in request.data:
            user.email = request.data['email']
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'password' in request.data:
            user.set_password(request.data['password'])
        if 'is_staff' in request.data:
            user.is_staff = request.data['is_staff']
        user.save()
        return Response(model_to_dict(user))