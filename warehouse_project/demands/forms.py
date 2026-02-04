from django import forms
from .models import Demand, DemandItem
from django.forms import inlineformset_factory

class DemandForm(forms.ModelForm):
    email_to = forms.EmailField(
        label="Recipient Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter recipient email',
            'required': True
        })
    )

    class Meta:
        model = Demand
        fields = ['demander_name', 'comment', 'email_to']
        widgets = {
            'demander_name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional comment'}),
        }

# Formset for multiple products, no delete checkbox
DemandItemFormSet = inlineformset_factory(
    Demand,
    DemandItem,
    fields=['product', 'quantity'],
    extra=1,
    can_delete=False
)
