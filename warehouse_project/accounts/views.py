from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from products.models import Product
from django.db import models
from django.db.models import F
from demands.models import Demand
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Todo
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid credentials or not admin'
            })

    return render(request, 'accounts/login.html')
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
# @login_required(login_url='login')
# def dashboard(request):
#     return render(request, 'accounts/dashboard.html')
@login_required
def dashboard(request):
    low_stock_products = Product.objects.filter(quantity__lt=F('min_stock'))
    todos = Todo.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'todos': todos,
        'low_stock_products': low_stock_products,
        'total_products': Product.objects.count(),
        'total_demands': Demand.objects.count(),
    }

    return render(request, 'accounts/dashboard.html', context)
@login_required
@require_POST
def add_todo(request):
    task = request.POST.get('task', '').strip()
    if task:
        todo = Todo.objects.create(user=request.user, task=task)
        return JsonResponse({'id': todo.id, 'task': todo.task})
    return JsonResponse({'error': 'Empty task'}, status=400)

@login_required
@require_POST
def edit_todo(request, todo_id):
    task = request.POST.get('task', '').strip()
    todo = Todo.objects.filter(id=todo_id, user=request.user).first()
    if todo and task:
        todo.task = task
        todo.save()
        return JsonResponse({'id': todo.id, 'task': todo.task})
    return JsonResponse({'error': 'Invalid task'}, status=400)

@login_required
@require_POST
def delete_todo(request, todo_id):
    Todo.objects.filter(id=todo_id, user=request.user).delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def delete_all_todos(request):
    Todo.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True})
@login_required
@require_POST
def toggle_todo(request, todo_id):
    todo = Todo.objects.filter(id=todo_id, user=request.user).first()
    if not todo:
        return JsonResponse({'error': 'Todo not found'}, status=404)
    todo.completed = not todo.completed
    todo.save()
    return JsonResponse({'id': todo.id, 'completed': todo.completed})