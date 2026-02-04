# reports/models.py
from django.db import models

class Report(models.Model):
    sender_name = models.CharField(max_length=100)
    email_to = models.EmailField()
    content = models.TextField()
    attachment = models.FileField(
        upload_to='reports/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report #{self.id}"
