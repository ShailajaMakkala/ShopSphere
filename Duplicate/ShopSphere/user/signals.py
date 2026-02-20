from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from .models import ProductReview

@receiver(post_save, sender=ProductReview)
@receiver(post_delete, sender=ProductReview)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    reviews = product.reviews.all()

# Calculate new average rating and total reviews
    if reviews.exists():
        average = reviews.aggregate(models.Avg('rating'))['rating__avg']
        count = reviews.count()
        product.average_rating = round(average, 1)
        product.total_reviews = count
    else:
        product.average_rating = 0
        product.total_reviews = 0

    product.save()