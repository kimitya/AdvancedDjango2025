from django.urls import path
from .views import *

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/execute/', ExecuteOrderView.as_view(), name='execute-order'),
    path('orders/my/', MyOrderListView.as_view(), name='my-orders'),

    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    # path('transactions/my/', MyTransactionListView.as_view(), name='my-transactions'),
]
