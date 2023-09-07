from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from . import models
from . import serializers
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework import status
from rest_framework.permissions import IsAdminUser, DjangoModelPermissions
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from django.forms import model_to_dict
# Create your views here.


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def managers(request):
    managers = Group.objects.get(name = 'Manager')
    if request.method == 'GET':
        manager_objects = list(User.objects.filter(groups__name = 'Manager').values())
        return Response(manager_objects)
    elif request.method == 'POST':
        username = request.data['username']
        user = get_object_or_404(User, username=username)
        managers.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)
       
    
    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def manager_removal(request, ids):
    user = get_object_or_404(User, id = ids)
    managers = Group.objects.get(name="Manager")
    managers.user_set.remove(user)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def delivery_crew(request):
    if request.user.groups.filter(name = 'Manager').exists():
        group = Group.objects.get(name= 'Delivery Crew')
        if request.method == 'GET':
            crew = list(User.objects.filter(groups__name = 'Delivery Crew').values())
            return Response(crew)
        elif request.method == 'POST':
            username = request.data['username']
            user = get_object_or_404(User, username=username)
            group.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['DELETE'])
def delivery_crew_removal(request, ids):
    user = get_object_or_404(User, id =ids)
    crew = Group.objects.get(name="Delivery Crew")
    crew.user_set.remove(user)
    return Response(status=status.HTTP_200_OK)



# @api_view(['GET','POST'])
# def menu_items(request):
#      if request.method == 'GET':
#           items = MenuItem.objects.select_related('category').all()
          
#           category_name = request.query_params.get('category')
#           to_price = request.query_params.get('to_price')
#           search = request.query_params.get('search')
#           ordering = request.query_params.get('ordering')
#           perpage = request.query_params.get('perpage', default=2)
#           page = request.query_params.get('page', default=1)

#           if category_name:
#                print(category_name)
#                items = items.filter(category__title=category_name)
#           if to_price:
#                items = items.filter(price__lte=to_price)
#           if search:
#                items = items.filter(title__icontains=search)
#           if ordering:
#                ordering_fields = ordering.split(",")
#                items = items.order_by(*ordering_fields)
#           paginator = Paginator(items, per_page=perpage)
#           try:
#                items = paginator.page(number=page)
#           except EmptyPage:
#                items = []
#           serialized_item = MenuItemSerializer(items, many=True)
#           return Response(serialized_item.data)
     
     
     
#      if request.method == 'POST':
#           serialized_item = MenuItemSerializer(data=request.data)
#           serialized_item.is_valid(raise_exception=True)
#           serialized_item.save()
#           return Response(serialized_item.data, status.HTTP_201_CREATED)



class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    permission_classes = [DjangoModelPermissions]
    

class CategoriesView(generics.ListCreateAPIView):
     queryset = models.Category.objects.all()
     serializer_class = serializers.CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    serializer_class = serializers.MenuItemSerializer
    permission_classes = [DjangoModelPermissions]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price', 'inventory']
  

    def get_queryset(self):
        queryset = models.MenuItem.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__title = category)
        return queryset


#make user readonly and automatically add the user to the field

class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = serializers.CartSerializer
    permission_classes =[IsAuthenticated]
    def get_queryset(self):
        return models.Cart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        menuitem = models.MenuItem.objects.filter(title = serializer.validated_data['menuitem'])
        serializer.validated_data['user'] = self.request.user
        serializer.validated_data['unit_price'] = menuitem[0].price
        price = serializer.validated_data['quantity'] * serializer.validated_data['unit_price']
        serializer.validated_data['price'] = price

        return super().perform_create(serializer)
    
    def destroy(self, request):
        
        try:
            queryset = self.get_queryset()
            queryset.delete()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    

#no customer group refactor so if IsAuthenticated is passed and user 
# does not belong to a group then assume customer

class OrderView(generics.ListCreateAPIView):
    serializer_class = serializers.OrderViewSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = models.Order.objects.all()   
        if self.request.user.groups.filter(name = 'Delivery Crew').exists():
            queryset = queryset.filter(delivery_crew = self.request.user.groups.filter(name = 'Delivery Crew'))
        else :
            queryset = queryset.filter(user = self.request.user)

        return queryset
        
        
        
    def create(self, request, *args, **kwargs):
        totals = 0
        cart = models.Cart.objects.filter(user = self.request.user)
        
        if cart:
            neworder = models.Order(user=self.request.user)
            neworder.save()
            for object in cart:
                order_item = models.OrderItem(order= self.request.user, menuitem=object.menuitem, quantity=object.quantity, unit_price = object.unit_price, price = object.price, order_ids = neworder )
                order_item.save()
                totals += object.price
                object.delete()
            neworder.total = totals
            neworder.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Order
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.groups.filter(name = 'Delivery Crew').exists():
            return serializers.DeliveryCrewOrderSerializer
        return serializers.OrderSerializer

    def retrieve(self, request, *args, **kwargs):
        order = self.queryset.objects.filter(id = self.kwargs['pk'])   
        if order[0].user == request.user:
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name ='Manager').exists():
            return super().destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    