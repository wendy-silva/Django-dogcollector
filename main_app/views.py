from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .models import Dog, Feeding, Toy
from .serializers import DogSerializer, FeedingSerializer, ToySerializer

# Define the home view
class Home(APIView):
  def get(self, request):
    content = {'message': 'Welcome to the dog-collector api home route!'}
    return Response(content)
  
class DogList(generics.ListCreateAPIView):
  queryset = Dog.objects.all()
  serializer_class = DogSerializer

class DogDetail(generics.RetrieveUpdateDestroyAPIView):
  queryset = Dog.objects.all()
  serializer_class = DogSerializer
  lookup_field = 'id'

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance)

    toys_not_associated = Toy.objects.exclude(id__in=instance.toys.all())
    toys_serializer = ToySerializer(toys_not_associated, many=True)

    return Response({
        'dog': serializer.data,
        'toys_not_associated': toys_serializer.data
    })
  
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