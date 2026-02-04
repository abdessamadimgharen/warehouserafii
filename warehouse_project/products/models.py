from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expiration_date = models.DateField(null=True, blank=True)
    supplier_name = models.CharField(max_length=100)
    min_stock = models.IntegerField()
    category = models.CharField(max_length=50, blank=True)  # optional category field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.total_price = (self.quantity or 0) * (self.price_per_unit or 0)
        super().save(*args, **kwargs)


