from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from .models import SalesOrder, Invoice
from .serializers import SalesOrderSerializer, InvoiceSerializer
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile

class SalesOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = SalesOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SalesOrder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# class SalesOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = SalesOrderSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return SalesOrder.objects.filter(user=self.request.user)
class SalesOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SalesOrder.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # Указываем, что обновление частичное (PATCH)
        return super().update(request, *args, **kwargs)


class GenerateInvoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(SalesOrder, id=order_id, user=request.user)

        if Invoice.objects.filter(order=order).exists():
            return Response({"error": "Invoice already exists"}, status=400)

        # Создание PDF
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

        # Создание Invoice
        invoice = Invoice(order=order)
        invoice.invoice_pdf.save(f"invoice_{order.id}.pdf", buffer)
        invoice.save()

        return Response({"message": "Invoice generated", "invoice": InvoiceSerializer(invoice).data})
