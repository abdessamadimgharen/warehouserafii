from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
                    'total_price': forms.NumberInput(attrs={'readonly': 'readonly'}),
                    'category': forms.TextInput(attrs={'placeholder': 'Enter product category'}),
                }