from django.db import models
from products.models import Product

WAREHOUSES = [
    ('CASA', 'CASA Warehouse'),
    ('EXTERN', 'External Warehouse'),
]

class Demand(models.Model):
    email_to = models.EmailField("Email to send demand")  # new email field
    demander_name = models.CharField(max_length=100)  # who fills the form
    comment = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Demand #{self.id} by {self.demander_name} - {self.email_to}"
class DemandItem(models.Model):
    demand = models.ForeignKey(Demand, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
