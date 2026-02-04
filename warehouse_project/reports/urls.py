from django.urls import path
from .views import *

urlpatterns = [
    path('send/', send_report, name='send_report'),
    path('list/', report_list, name='report_list'),
    path('reports/delete/<int:pk>/', report_delete, name='report_delete'),

]
