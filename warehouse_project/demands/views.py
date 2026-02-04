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
from reportlab.lib.colors import black, lightgrey
from reportlab.lib.units import inch
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
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Facture - Demand #{demand.id}</title>

                <style>
                    body {{
                        font-family: "Segoe UI", Arial, sans-serif;
                        background-color: #f5f6fa;
                        margin: 0;
                        padding: 30px;
                    }}

                    .invoice-container {{
                        max-width: 800px;
                        margin: auto;
                        background: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
                    }}

                    .invoice-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 2px solid #eee;
                        padding-bottom: 15px;
                        margin-bottom: 20px;
                    }}

                    .invoice-header h2 {{
                        margin: 0;
                        color: #2c3e50;
                    }}

                    .invoice-header span {{
                        color: #888;
                        font-size: 14px;
                    }}

                    .info {{
                        margin-bottom: 20px;
                    }}

                    .info p {{
                        margin: 5px 0;
                        color: #444;
                    }}

                    .info strong {{
                        color: #000;
                    }}

                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 15px;
                    }}

                    table thead {{
                        background-color: #f0f2f5;
                    }}

                    table th, table td {{
                        padding: 12px;
                        border: 1px solid #ddd;
                        text-align: left;
                    }}

                    table th {{
                        font-weight: 600;
                        color: #333;
                    }}

                    table tbody tr:nth-child(even) {{
                        background-color: #fafafa;
                    }}

                    .footer {{
                        margin-top: 30px;
                        text-align: center;
                        color: #777;
                        font-size: 13px;
                    }}

                    .print-btn {{
                        margin-top: 25px;
                        text-align: right;
                    }}

                    .print-btn button {{
                        background-color: #0d6efd;
                        color: white;
                        border: none;
                        padding: 10px 18px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                    }}

                    .print-btn button:hover {{
                        background-color: #0b5ed7;
                    }}

                    @media print {{
                        body {{
                            background: none;
                            padding: 0;
                        }}

                        .invoice-container {{
                            box-shadow: none;
                            border-radius: 0;
                        }}

                        .print-btn {{
                            display: none;
                        }}
                    }}
                </style>
            </head>

            <body>
                <div class="invoice-container">

                    <div class="invoice-header">
                        <h2>Facture : Silda</h2>
                        <span>Demand #{demand.id}</span>
                    </div>

                    <div class="info">
                        <p><strong>Demander:</strong> {demand.demander_name}</p>
                        <p><strong>Receiver:</strong> {demand.email_to}</p>
                        <p><strong>Date:</strong> {demand.date}</p>
                        <p><strong>Comment:</strong> {demand.comment}</p>
                    </div>

                    <h3>Products</h3>

                    <table>
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Quantity</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            for product_name, quantity in items_data:
                facture_html += f"""
                            <tr>
                                <td>{product_name}</td>
                                <td>{quantity}</td>
                            </tr>
                """

            facture_html += """
                        </tbody>
                    </table>

                    <div class="print-btn">
                        <button onclick="window.print()">🖨️ Print Facture</button>
                    </div>

                    <div class="footer">
                        Generated automatically • Warehouse Management System
                    </div>

                </div>
            </body>
            </html>
            """


            with open(facture_file, 'w', encoding='utf-8') as f:
                f.write(facture_html)

            # Generate PDF facture
            pdf_file = facture_dir / f'demand_{demand.id}.pdf'


            c = canvas.Canvas(str(pdf_file), pagesize=letter)
            width, height = letter

            # Title background
            c.setFillColor(lightgrey)
            c.rect(0, height - 1.2 * inch, width, 1.2 * inch, fill=1)

            # Title text
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(1 * inch, height - 0.8 * inch, f"FACTURE #{demand.id}")

            # Info section
            c.setFont("Helvetica", 12)
            y = height - 1.6 * inch
            c.drawString(1 * inch, y, f"Demander: {demand.demander_name}")
            y -= 0.25 * inch
            c.drawString(1 * inch, y, f"Date: {demand.date}")
            y -= 0.25 * inch
            c.drawString(1 * inch, y, f"Comment: {demand.comment}")

            # Table header
            y -= 0.4 * inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1 * inch, y, "Product")
            c.drawString(4 * inch, y, "Quantity")

            c.line(1 * inch, y - 5, 7.5 * inch, y - 5)

            # Table rows
            c.setFont("Helvetica", 11)
            y -= 0.3 * inch
            for product_name, quantity in items_data:
                c.drawString(1 * inch, y, product_name)
                c.drawString(4 * inch, y, str(quantity))
                y -= 0.25 * inch

            # Footer
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(width / 2, 0.75 * inch, "Generated by Warehouse Management System")

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
    demands = Demand.objects.prefetch_related(
        Prefetch('items', queryset=DemandItem.objects.select_related('product'))
    ).all().order_by('-date', '-id')

    product_query = request.GET.get('product', '')
    date_query = request.GET.get('date', '')

    if product_query:
        demands = demands.filter(
            items__product__name__icontains=product_query
        ).distinct() 

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
