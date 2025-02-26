from rest_framework import serializers
from .models import Order, Transaction

class OrderSerializer(serializers.ModelSerializer):
    # user = serializers.ReadOnlyField(source='user.id')
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Order
        fields = ('id', 'user', 'product', 'product_name', 'order_type', 'quantity', 'price', 'status', 'created_at', 'updated_at')

class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    order_details = OrderSerializer(source='order', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'order', 'order_details', 'executed_price', 'executed_at')
