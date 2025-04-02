from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('allauth.urls')), 
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-group-expense/', views.add_group_expense, name='add_group_expense'),
    path('group-expenses/', views.group_expense_list, name='group_expense_list'),
] 