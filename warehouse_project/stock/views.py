from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StockMovement
from .forms import StockMovementForm
from products.models import Product
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.db.models import Sum
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from datetime import datetime, date
from django.http import HttpResponse
import io
from reportlab.pdfgen import canvas
@login_required
def stock_create(request):
    form = StockMovementForm(request.POST or None)
    if form.is_valid():
        stock_movement = form.save()
        product = stock_movement.product
        if stock_movement.movement_type == 'ENTRANCE':
            product.quantity += stock_movement.quantity
        else:  
            product.quantity -= stock_movement.quantity
        product.save()
        return redirect('stock_list')

    return render(request, 'stock/stock_form.html', {'form': form})

@login_required
def stock_list(request):
    movements = StockMovement.objects.select_related('product').all().order_by('-date', '-id')

    date_filter = request.GET.get('date', '')
    product_filter = request.GET.get('product', '')
    category_query = request.GET.get('category', '')

    if date_filter:
        movements = movements.filter(date__date=date_filter) 
    if product_filter:
        if product_filter.isdigit():
            movements = movements.filter(product__id=int(product_filter))
        else:
            movements = movements.filter(product__name__icontains=product_filter)

    if category_query:
        movements = movements.filter(product__category__icontains=category_query)

    context = {
        'movements': movements,
        'date_filter': date_filter,
        'product_filter': product_filter,
        'category_query': category_query,
    }

    return render(request, 'stock/stock_list.html', context)


@login_required
def daily_stock(request):
    selected_date = request.GET.get('date') or date.today().isoformat()  
    daily_data = []

    total_entrances_all = 0
    total_exits_all = 0

    products = Product.objects.all()

    for p in products:
        movements = StockMovement.objects.filter(product=p, date__date=selected_date)

        entrances = movements.filter(
            movement_type='ENTRANCE'
        ).aggregate(total=Sum('quantity'))['total'] or 0

        exits = movements.filter(
            movement_type='EXIT'
        ).aggregate(total=Sum('quantity'))['total'] or 0

        if entrances > 0 or exits > 0 or selected_date == date.today().isoformat():
            daily_data.append({
                'product': p,
                'total_entrances': entrances,
                'total_exits': exits,
                'final_stock': p.quantity,
            })
            total_entrances_all += entrances
            total_exits_all += exits

    if 'export_pdf' in request.GET:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, f"Daily Stock Report - {selected_date}")
        y = 750
        p.drawString(50, y, "Product")
        p.drawString(200, y, "Entrances")
        p.drawString(300, y, "Exits")
        p.drawString(400, y, "Final Stock")
        y -= 25
        for d in daily_data:
            p.drawString(50, y, d['product'].name)
            p.drawString(200, y, str(d['total_entrances']))
            p.drawString(300, y, str(d['total_exits']))
            p.drawString(400, y, str(d['final_stock']))
            y -= 20
        p.drawString(50, y-10, f"TOTALS: Entrances {total_entrances_all} | Exits {total_exits_all}")
        p.showPage()
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

    return render(request, 'stock/daily_stock.html', {
        'daily_data': daily_data,
        'selected_date': selected_date,
        'total_entrances_all': total_entrances_all,
        'total_exits_all': total_exits_all,
    })


@login_required
def product_stock_movements(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    movements = StockMovement.objects.filter(
        product=product
    ).order_by('-date')

    stock = 0
    for m in movements:
        if m.movement_type == 'ENTRANCE':
            stock += m.quantity
        else:
            stock -= m.quantity

    return render(request, 'stock/product_stock_movements.html', {
        'product': product,
        'movements': movements,
        'final_stock': stock
    })

@login_required
def stock_delete(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    if request.method == 'POST':
        movement.delete()
        return redirect('stock_list') 
    return render(request, 'stock/stock_confirm_delete.html', {'movement': movement})