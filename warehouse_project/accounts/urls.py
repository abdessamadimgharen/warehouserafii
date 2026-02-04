from django.urls import path
from .views import login_view, logout_view, dashboard
from . import views
urlpatterns = [
    path('', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
     path('todos/add/', views.add_todo, name='add_todo'),
    path('todos/edit/<int:todo_id>/', views.edit_todo, name='edit_todo'),
    path('todos/delete/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('todos/delete_all/', views.delete_all_todos, name='delete_all_todos'),
path('todos/toggle/<int:todo_id>/', views.toggle_todo, name='toggle_todo'),
]
