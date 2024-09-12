from django.urls import path
from .views import Home, DogList, DogDetail, FeedingListCreate, FeedingDetail, ToyList, ToyDetail

urlpatterns = [
  path('', Home.as_view(), name='home'),
  # new routes below 
  path('dogs/', DogList.as_view(), name='dog-list'),
  path('dogs/<int:id>/', DogDetail.as_view(), name='dog-detail'),
  path('dogs/<int:dog_id>/feedings/', FeedingListCreate.as_view(), name='feeding-list-create'),
	path('dogs/<int:dog_id>/feedings/<int:id>/', FeedingDetail.as_view(), name='feeding-detail'),
  path('toys/', ToyList.as_view(), name='toy-list'),
  path('toys/<int:id>/', ToyDetail.as_view(), name='toy-detail'),
]