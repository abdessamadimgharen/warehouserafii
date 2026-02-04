from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm
from django.contrib import messages
from django.db.models import Q
from stock.models import StockMovement
@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save(commit=False)

        initial_quantity = product.quantity or 0
        product.quantity = 0
        product.save()

        if initial_quantity > 0:
            from stock.models import StockMovement
            StockMovement.objects.create(
                product=product,
                movement_type='ENTRANCE',
                quantity=initial_quantity
            )

            product.quantity = initial_quantity
            product.save()

        return redirect('product_list')

    return render(request, 'products/product_form.html', {'form': form})
@login_required
def product_list(request):
    from django.shortcuts import get_object_or_404
    from stock.models import Product, StockMovement

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        entrance_qty = request.POST.get('entrance_qty')
        exit_qty = request.POST.get('exit_qty')

        product = get_object_or_404(Product, id=product_id)

        if entrance_qty and int(entrance_qty) > 0:
            product.quantity += int(entrance_qty)
            StockMovement.objects.create(
                product=product,
                movement_type='ENTRANCE',
                quantity=int(entrance_qty)
            )

        if exit_qty and int(exit_qty) > 0:
            if product.quantity >= int(exit_qty):
                product.quantity -= int(exit_qty)
                StockMovement.objects.create(
                    product=product,
                    movement_type='EXIT',
                    quantity=int(exit_qty)
                )

        product.save()
        return redirect('product_list')

    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    products = Product.objects.all().order_by('-created_at')  

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category__icontains=category)

    categories = Product.objects.values_list('category', flat=True).distinct()

    return render(request, 'products/product_list.html', {
        'products': products,
        'query': query,            
        'categories': categories,  
        'selected_category': category
    })

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)

    if form.is_valid():
        form.save()
        return redirect('product_list')

    return render(request, 'products/product_form.html', {'form': form})
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product '{product.name}' deleted successfully!")

        return redirect('product_list')

    return render(request, 'products/product_confirm_delete.html', {'product': product})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from products.models import Product

@login_required
def suppliers_list(request):
    product_query = request.GET.get('product', '').strip()     
    supplier_query = request.GET.get('supplier', '').strip()

    products = Product.objects.all().order_by('supplier_name', 'name')

    if product_query:
        products = products.filter(name__icontains=product_query)

    if supplier_query:
        products = products.filter(supplier_name__icontains=supplier_query)

    return render(request, 'products/suppliers_list.html', {
        'products': products,
        'products_query': product_query, 
        'supplier_query': supplier_query,
    })
