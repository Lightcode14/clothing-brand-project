from django.db import models

class Products(models.Model):
   name= models.CharField()
   image= models.ImageField(upload_to="products")
   color = models.CharField(max_length=50, blank=True)
   price = models.DecimalField(max_digits=10, decimal_places=2)
   old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
   is_on_sale = models.BooleanField(default=False)
   is_active = models.BooleanField(default=True)
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
        return self.name

