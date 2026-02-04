from django.db import models
from products.models import Product

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('ENTRANCE', 'Entrance'),
        ('EXIT', 'Exit'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movement_type} - {self.product.name} - {self.quantity}"
