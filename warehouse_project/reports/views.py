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
            <html>
            <head>
                <meta charset="utf-8">
                <title>Report #{report.id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    img {{ max-width: 400px; margin-top: 10px; }}
                    @media print {{
                        #print-button {{ display: none; }}
                    }}
                </style>
            </head>
            <body>

                <h2>Report #{report.id}</h2>

                <p><strong>Date:</strong> {report.created_at}</p>
                <p><strong>Sender:</strong> {report.sender_name}</p>
                <p><strong>Email To:</strong> {report.email_to}</p>

                <hr>

                <h3>Report Content</h3>
                <p>{report.content}</p>

                {attachment_html}

                <button id="print-button" onclick="window.print()">Print</button>

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
