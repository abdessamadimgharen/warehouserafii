from django.urls import path
from .views import *

urlpatterns = [
    path('', stock_list, name='stock_list'),
    path('add/', stock_create, name='stock_add'),
    path('daily/', daily_stock, name='daily_stock'), 
    path('product/<int:product_id>/', product_stock_movements, name='product_stock_movements'),
    path('movements/delete/<int:pk>/', stock_delete, name='stock_delete'),
]
