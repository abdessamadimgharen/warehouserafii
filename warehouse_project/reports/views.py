from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from pathlib import Path
from django.contrib import messages
from .forms import ReportForm
from .models import Report
from django.core.mail import EmailMessage


@login_required
def send_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save()

            email = EmailMessage(
                subject=f"Report from {report.sender_name}",
                body=report.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[report.email_to],
            )

            if report.attachment:
                email.attach_file(report.attachment.path)

            email.send(fail_silently=False)

            media_root = Path(settings.MEDIA_ROOT)
            facture_dir = media_root / 'factures'
            facture_dir.mkdir(parents=True, exist_ok=True)

            facture_file = facture_dir / f'report_{report.id}.html'

            attachment_html = ""
            if report.attachment:
                if str(report.attachment).lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                    attachment_html = f"""
                    <p><strong>Attachment:</strong></p>
                    <img src="{settings.MEDIA_URL}{report.attachment}" alt="Attachment">
                    """
                else:
                    attachment_html = f"""
                    <p><strong>Attachment:</strong> 
                        <a href="{settings.MEDIA_URL}{report.attachment}" target="_blank">
                            {report.attachment.name.split('/')[-1]}
                        </a>
                    </p>
                    """
            facture_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Report #{report.id}</title>

                <style>
                    body {{
                        font-family: "Segoe UI", Arial, sans-serif;
                        background-color: #f5f6fa;
                        margin: 0;
                        padding: 30px;
                    }}

                    .report-container {{
                        max-width: 800px;
                        margin: auto;
                        background: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
                    }}

                    .report-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 2px solid #eee;
                        padding-bottom: 15px;
                        margin-bottom: 20px;
                    }}

                    .report-header h2 {{
                        margin: 0;
                        color: #2c3e50;
                    }}

                    .report-header span {{
                        color: #888;
                        font-size: 14px;
                    }}

                    .info p {{
                        margin: 6px 0;
                        color: #444;
                    }}

                    .info strong {{
                        color: #000;
                    }}

                    hr {{
                        border: none;
                        border-top: 1px solid #eee;
                        margin: 25px 0;
                    }}

                    .content {{
                        color: #333;
                        line-height: 1.6;
                    }}

                    .content h3 {{
                        margin-top: 0;
                        color: #2c3e50;
                    }}

                    .attachment {{
                        margin-top: 20px;
                    }}

                    .attachment img {{
                        max-width: 100%;
                        border-radius: 6px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                        margin-top: 10px;
                    }}

                    .print-btn {{
                        margin-top: 25px;
                        text-align: right;
                    }}

                    .print-btn button {{
                        background-color: #198754;
                        color: #fff;
                        border: none;
                        padding: 10px 18px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                    }}

                    .print-btn button:hover {{
                        background-color: #157347;
                    }}

                    @media print {{
                        body {{
                            background: none;
                            padding: 0;
                        }}

                        .report-container {{
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
                <div class="report-container">

                    <div class="report-header">
                        <h2>Report</h2>
                        <span>#{report.id}</span>
                    </div>

                    <div class="info">
                        <p><strong>Date:</strong> {report.created_at}</p>
                        <p><strong>Sender:</strong> {report.sender_name}</p>
                        <p><strong>Email To:</strong> {report.email_to}</p>
                    </div>

                    <hr>

                    <div class="content">
                        <h3>Report Content</h3>
                        <p>{report.content}</p>
                    </div>

                    <div class="attachment">
                        {attachment_html}
                    </div>

                    <div class="print-btn">
                        <button onclick="window.print()">🖨️ Print Report</button>
                    </div>

                </div>
            </body>
            </html>
            """


            with open(facture_file, 'w', encoding='utf-8') as f:
                f.write(facture_html)

            messages.success(request, "Report sent successfully with attachment.")
            return redirect('report_list')

    else:
        form = ReportForm()

    return render(request, 'reports/send_report.html', {'form': form})

@login_required
def report_list(request):
    reports = Report.objects.all().order_by('-created_at', '-id')
    return render(request, 'reports/report_list.html', {
        'reports': reports,
        'MEDIA_URL': settings.MEDIA_URL
    })


@login_required
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        report.delete()
        return redirect('report_list')
    return render(request, 'reports/confirm_delete.html', {
        'report': report
    })
