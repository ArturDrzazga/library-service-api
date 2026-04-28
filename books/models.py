from django.db import models

class Book(models.Model):
    class CoverType(models.TextChoices):
        HARD = 'HARD', "Hard"
        SOFT = 'SOFT', "Soft"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(
        max_length=4,
        choices=CoverType.choices,
        default=CoverType.SOFT,
        )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)
