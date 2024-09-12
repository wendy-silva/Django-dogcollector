from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Dog, Feeding, Toy
from .serializers import DogSerializer, FeedingSerializer, ToySerializer, UserSerializer

# Define the home view
class Home(APIView):
  def get(self, request):
    content = {'message': 'Welcome to the dog-collector api home route!'}
    return Response(content)
  
class CreateUserView(generics.CreateAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer

  def create(self, request, *args, **kwargs):
    response = super().create(request, *args, **kwargs)
    user = User.objects.get(username=response.data['username'])
    refresh = RefreshToken.for_user(user)
    return Response({
      'refresh': str(refresh),
      'access': str(refresh.access_token),
      'user': response.data
    })

# User Login
class LoginView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
      refresh = RefreshToken.for_user(user)
      return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user).data
      })
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# User Verification
class VerifyUserView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    user = User.objects.get(username=request.user)  # Fetch user profile
    refresh = RefreshToken.for_user(request.user)  # Generate new refresh token
    return Response({
      'refresh': str(refresh),
      'access': str(refresh.access_token),
      'user': UserSerializer(user).data
    })
  
class DogList(generics.ListCreateAPIView):
  serializer_class = DogSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
      user = self.request.user
      return Dog.objects.filter(user=user)

  def perform_create(self, serializer):
      serializer.save(user=self.request.user)
  
class DogDetail(generics.RetrieveUpdateDestroyAPIView):
  serializer_class = DogSerializer
  lookup_field = 'id'

  def get_queryset(self):
    user = self.request.user
    return Dog.objects.filter(user=user)

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance)

    toys_not_associated = Toy.objects.exclude(id__in=instance.toys.all())
    toys_serializer = ToySerializer(toys_not_associated, many=True)

    return Response({
        'dog': serializer.data,
        'toys_not_associated': toys_serializer.data
    })

  def perform_update(self, serializer):
    dog = self.get_object()
    if dog.user != self.request.user:
        raise PermissionDenied({"message": "You do not have permission to edit this dog."})
    serializer.save()

  def perform_destroy(self, instance):
    if instance.user != self.request.user:
        raise PermissionDenied({"message": "You do not have permission to delete this dog."})
    instance.delete()
  
class FeedingListCreate(generics.ListCreateAPIView):
  serializer_class = FeedingSerializer

  def get_queryset(self):
    dog_id = self.kwargs['dog_id']
    return Feeding.objects.filter(dog_id=dog_id)

  def perform_create(self, serializer):
    dog_id = self.kwargs['dog_id']
    dog = Dog.objects.get(id=dog_id)
    serializer.save(dog=dog)
    
class FeedingDetail(generics.RetrieveUpdateDestroyAPIView):
  serializer_class = FeedingSerializer
  lookup_field = 'id'

  def get_queryset(self):
    dog_id = self.kwargs['dog_id']
    return Feeding.objects.filter(dog_id=dog_id)
  
class ToyList(generics.ListCreateAPIView):
  queryset = Toy.objects.all()
  serializer_class = ToySerializer

class ToyDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Toy.objects.all()
  serializer_class = ToySerializer
  lookup_field = 'id'
  
class AddToyToDog(APIView):
  def post(self, request, dog_id, toy_id):
    dog = Dog.objects.get(id=dog_id)
    toy = Toy.objects.get(id=toy_id)
    dog.toys.add(toy)
    return Response({'message': f'Toy {toy.name} added to Dog {dog.name}'})

class RemoveToyFromDog(APIView):
  def post(self, request, dog_id, toy_id):
    dog = Dog.objects.get(id=dog_id)
    toy = Toy.objects.get(id=toy_id)
    dog.toys.remove(toy)
    return Response({'message': f'Toy {toy.name} removed from Dog {dog.name}'})