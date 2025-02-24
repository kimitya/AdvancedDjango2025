from rest_framework import serializers
from .models import SalesOrder, Invoice

class SalesOrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = SalesOrder
        fields = ('id', 'user', 'product', 'product_name', 'quantity', 'total_price', 'status', 'created_at', 'updated_at')

class InvoiceSerializer(serializers.ModelSerializer):
    order_details = SalesOrderSerializer(source='order', read_only=True)

    class Meta:
        model = Invoice
        fields = ('id', 'order', 'order_details', 'invoice_pdf', 'created_at')
