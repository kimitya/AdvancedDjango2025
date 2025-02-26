from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from .models import SalesOrder, Invoice
from .serializers import SalesOrderSerializer, InvoiceSerializer
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile

from users.permissions import *




# class SalesOrderListCreateView(generics.ListCreateAPIView):
#     serializer_class = SalesOrderSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return SalesOrder.objects.filter(user=self.request.user)
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
#
#     @property
#     def permission_classes(self):
#         if self.request.method == 'GET':
#             return [permissions.AllowAny]
#         return [IsCustomer | IsSalesRepresentative | IsAdmin]

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [permissions.AllowAny()]
    #     return [IsCustomer() or IsSalesRepresentative() or IsAdmin()]

class SalesOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = SalesOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     return SalesOrder.objects.filter(user=self.request.user)
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.has_perm(user, IsCustomer):
    #         return SalesOrder.objects.filter(user=user)
    #     elif user.has_perm(user, IsSalesRepresentative):
    #         return SalesOrder.objects.filter(product__user=user)
    #
    #     return SalesOrder.objects.none()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == "customer":
            return SalesOrder.objects.filter(user=user)
        elif user.is_authenticated and user.role == "sales":
            return SalesOrder.objects.filter(product__user=user)
        return SalesOrder.objects.none()


    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        if quantity > product.stock:
            raise serializers.ValidationError({'quantity': 'Requested quantity exceeds available stock.'})

        total_price = product.price * quantity
        serializer.save(user=self.request.user, total_price=total_price)

    @property
    def permission_classes(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny]
        return [IsCustomer | IsSalesRepresentative | IsAdmin]



    # class SalesOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = SalesOrderSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return SalesOrder.objects.filter(user=self.request.user)
# class SalesOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = SalesOrder.objects.all()
#     serializer_class = SalesOrderSerializer
#     permission_classes = [IsOwner]
#
#     def get_queryset(self):
#         return SalesOrder.objects.filter(user=self.request.user)
#
#     def update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return super().update(request, *args, **kwargs)
#
#     @property
#     def permission_classes(self):
#         if self.request.method == 'GET':
#             return [permissions.AllowAny]
#         return [IsCustomer | IsSalesRepresentative | IsAdmin]

class SalesOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    # permission_classes = [IsOwner]



    def update(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user

        if user != order.product.user:
            return Response({'error': 'You do not have permission to update this order'},
                            status=status.HTTP_403_FORBIDDEN)

        old_status = order.status

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        order.refresh_from_db()

        if old_status != order.status:
            product = order.product
            if order.status in ['approved', 'shipped', 'delivered']:
                if product.stock >= order.quantity:
                    product.stock -= order.quantity
                    product.save()
                else:
                    return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)


    @property
    def permission_classes(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny]
        return [IsCustomer | IsSalesRepresentative | IsAdmin]



class GenerateInvoiceView(APIView):
    permission_classes = [IsSalesRepresentative | IsAdmin]

    def post(self, request, order_id):
        order = get_object_or_404(SalesOrder, id=order_id, user=request.user)

        if request.user != order.product.user:
            return Response({"error": "You do not have permission to generate an invoice for this order."}, status=403)

        if Invoice.objects.filter(order=order).exists():
            return Response({"error": "Invoice already exists"}, status=400)

        buffer = ContentFile(b"")
        pdf = canvas.Canvas(buffer)
        pdf.drawString(100, 750, f"Invoice for Order #{order.id}")
        pdf.drawString(100, 730, f"Customer: {order.user.username}")
        pdf.drawString(100, 710, f"Product: {order.product.name}")
        pdf.drawString(100, 690, f"Quantity: {order.quantity}")
        pdf.drawString(100, 670, f"Total Price: ${order.total_price}")
        pdf.drawString(100, 650, f"Status: {order.status}")
        pdf.save()
        buffer.seek(0)

        invoice = Invoice(order=order)
        invoice.invoice_pdf.save(f"invoice_{order.id}.pdf", buffer)
        invoice.save()

        return Response({"message": "Invoice generated", "invoice": InvoiceSerializer(invoice).data})