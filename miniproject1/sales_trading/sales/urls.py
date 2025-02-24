from django.urls import path
from .views import SalesOrderListCreateView, SalesOrderDetailView, GenerateInvoiceView

urlpatterns = [
    path('orders/', SalesOrderListCreateView.as_view(), name='salesorder-list'),
    path('orders/<int:pk>/', SalesOrderDetailView.as_view(), name='salesorder-detail'),
    path('orders/<int:order_id>/invoice/', GenerateInvoiceView.as_view(), name='generate-invoice'),
]