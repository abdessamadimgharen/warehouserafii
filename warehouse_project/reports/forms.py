from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['sender_name', 'email_to', 'content', 'attachment']
        widgets = {
            'sender_name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email_to': forms.EmailInput(attrs={'placeholder': 'Recipient email'}),
            'content': forms.Textarea(attrs={'rows': 4}),
        }
