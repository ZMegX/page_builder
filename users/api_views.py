from rest_framework import generics, permissions
from users.models import Order
from menus.serializers import OrderSerializer

class CustomerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')

class CustomerOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

class RestaurantOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'restaurant_profile') and user.restaurant_profile:
            return Order.objects.filter(restaurant=user.restaurant_profile).order_by('-created_at')
        return Order.objects.none()

class RestaurantOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'restaurant_profile') and user.restaurant_profile:
            return Order.objects.filter(restaurant=user.restaurant_profile)
        return Order.objects.none()
