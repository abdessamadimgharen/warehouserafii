from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Demand, DemandItem
from .forms import DemandForm, DemandItemFormSet
from products.models import Product
from django.core.mail import send_mail
from django.conf import settings
from .models import Demand
import os
from django.conf import settings
from pathlib import Path
from django.db.models import Prefetch
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
@login_required
def create_demand(request):
    products_list = Product.objects.all()  

    if request.method == 'POST':
        form = DemandForm(request.POST)
        if form.is_valid():

            items_data = []
            total_forms = int(request.POST.get('items-TOTAL_FORMS', 0))
            for i in range(total_forms):
                product_name = request.POST.get(f'items-{i}-product')
                quantity = request.POST.get(f'items-{i}-quantity')
                if product_name and quantity and int(quantity) > 0:
                    items_data.append((product_name.strip(), int(quantity)))

            if not items_data:
                messages.error(request, "You must add at least one product before sending the demand.")
                return redirect('demand_add')

            demand = form.save()

            for product_name, quantity in items_data:
                product_obj, _ = Product.objects.get_or_create(
                    name=product_name,
                    defaults={
                        'quantity': 0,
                        'price_per_unit': 0,
                        'supplier_name': '',
                        'min_stock': 0,
                        'expiration_date': None,
                    }
                )
                DemandItem.objects.create(
                    demand=demand,
                    product=product_obj,
                    quantity=quantity
                )

            message = f"Demander: {demand.demander_name}\nDate: {demand.date}\nComment: {demand.comment}\nProducts:\n"
            for product_name, quantity in items_data:
                message += f"- {product_name} | Quantity: {quantity}\n"

            send_mail(
                subject=f"New Demand #{demand.id}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[demand.email_to],
                fail_silently=False,
            )

            demand.sent = True
            demand.save(update_fields=['sent'])

            # Generate HTML facture
            media_root = Path(settings.MEDIA_ROOT)
            facture_dir = media_root / 'factures'
            facture_dir.mkdir(parents=True, exist_ok=True)
            facture_file = facture_dir / f'demand_{demand.id}.html'

            facture_html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <title>Facture - Demand #{demand.id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h2 {{ color: #333; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    @media print {{ #print-button {{ display: none; }} }}
                </style>
            </head>
            <body>
                <h2>Facture - Demand #{demand.id}</h2>
                <p><strong>Demander:</strong> {demand.demander_name}</p>
                <p><strong>Receiver:</strong> {demand.email_to}</p>
                <p><strong>Date:</strong> {demand.date}</p>
                <p><strong>Comment:</strong> {demand.comment}</p>

                <h3>Products</h3>
                <table>
                    <thead>
                        <tr><th>Product</th><th>Quantity</th></tr>
                    </thead>
                    <tbody>
            """
            for product_name, quantity in items_data:
                facture_html += f"<tr><td>{product_name}</td><td>{quantity}</td></tr>"
            facture_html += """
                    </tbody>
                </table>
                <br>
                <button id="print-button" onclick="window.print()">🖨️ Print Facture</button>
            </body>
            </html>
            """

            with open(facture_file, 'w', encoding='utf-8') as f:
                f.write(facture_html)

            # Generate PDF facture
            pdf_file = facture_dir / f'demand_{demand.id}.pdf'
            c = canvas.Canvas(str(pdf_file), pagesize=letter)
            width, height = letter

            c.setFont("Helvetica-Bold", 16)
            c.drawString(1 * inch, height - 1 * inch, f"Facture - Demand #{demand.id}")

            c.setFont("Helvetica", 12)
            c.drawString(1 * inch, height - 1.3 * inch, f"Demander: {demand.demander_name}")
            c.drawString(1 * inch, height - 1.5 * inch, f"Date: {demand.date}")
            c.drawString(1 * inch, height - 1.7 * inch, f"Comment: {demand.comment}")

            c.setFont("Helvetica-Bold", 12)
            c.drawString(1 * inch, height - 2.1 * inch, "Products:")
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1 * inch, height - 2.3 * inch, "Product")
            c.drawString(4 * inch, height - 2.3 * inch, "Quantity")

            y = height - 2.5 * inch
            c.setFont("Helvetica", 11)
            for product_name, quantity in items_data:
                c.drawString(1 * inch, y, product_name)
                c.drawString(4 * inch, y, str(quantity))
                y -= 0.2 * inch

            c.save()

            messages.success(request, f"Demand #{demand.id} sent successfully!")
            return redirect('demand_list')

    else:
        form = DemandForm()

    return render(request, 'demands/demand_form.html', {
        'form': form,
        'products': products_list
    })
from django.conf import settings

from django.db.models import Prefetch


from django.db.models import Q

from django.db.models import Prefetch, Q

@login_required
def demand_list(request):
    # Start with all demands and prefetch items + product
    demands = Demand.objects.prefetch_related(
        Prefetch('items', queryset=DemandItem.objects.select_related('product'))
    ).all().order_by('-date', '-id')

    # Get search parameters
    product_query = request.GET.get('product', '')
    date_query = request.GET.get('date', '')

    # Filter by product name
    if product_query:
        demands = demands.filter(
            items__product__name__icontains=product_query
        ).distinct()  # distinct to avoid duplicates if multiple products match

    # Filter by date
    if date_query:
        demands = demands.filter(date=date_query)

    return render(request, 'demands/demand_list.html', {
        'demands': demands,
        'MEDIA_URL': settings.MEDIA_URL,
        'product_query': product_query,
        'date_query': date_query,
    })

from django.shortcuts import get_object_or_404

@login_required
def demand_delete(request, pk):
    """
    Delete a demand and all its items
    """
    demand = get_object_or_404(Demand, pk=pk)
    if request.method == 'POST':
        demand.delete()
        return redirect('demand_list')
    return render(request, 'demands/demand_confirm_delete.html', {'demand': demand})
