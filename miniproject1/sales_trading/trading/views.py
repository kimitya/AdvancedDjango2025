from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from .models import Order, Transaction
from .serializers import OrderSerializer, TransactionSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)  # Фильтруем заказы только текущего пользователя

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class ExecuteOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user, status='pending')
            executed_price = order.price  # В реальной системе можно менять цену в зависимости от рынка
            transaction = Transaction.objects.create(order=order, executed_price=executed_price, executed_at=now())

            order.status = 'completed'
            order.save()

            return Response({"message": "Order executed", "transaction": TransactionSerializer(transaction).data})
        except Order.DoesNotExist:
            return Response({"error": "Order not found or already completed"}, status=400)



class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список всех транзакций пользователя.
        Можно фильтровать по параметрам ?product=1 или ?date=YYYY-MM-DD.
        """
        queryset = Transaction.objects.filter(order__user=self.request.user)
        product_id = self.request.query_params.get('product')
        date = self.request.query_params.get('date')

        if product_id:
            queryset = queryset.filter(order__product_id=product_id)
        if date:
            queryset = queryset.filter(executed_at__date=date)

        return queryset

class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(order__user=self.request.user)

