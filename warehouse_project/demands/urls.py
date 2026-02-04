from django.urls import path
from .views import *

urlpatterns = [
    path('', demand_list, name='demand_list'),
   path('add/', create_demand, name='demand_add'),
   path('delete/<int:pk>/', demand_delete, name='demand_delete'),
]
