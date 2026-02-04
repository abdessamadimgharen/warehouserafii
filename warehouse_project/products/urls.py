from django.urls import path
from .views import (
    product_list,
    product_create,
    product_update,
    product_delete,
    suppliers_list,
)

urlpatterns = [
    path('', product_list, name='product_list'),
    path('add/', product_create, name='product_add'),
    path('<int:pk>/edit/', product_update, name='product_update'),
    path('<int:pk>/delete/', product_delete, name='product_delete'),
    path('suppliers/', suppliers_list, name='suppliers_list'),
]
