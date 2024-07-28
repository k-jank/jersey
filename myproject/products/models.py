from django.db import models

# Create your models here.

class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=50)
    rating = models.CharField(max_length=50, blank=True, null=True)
    sold = models.CharField(max_length=50, blank=True, null=True)
    link = models.URLField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
