from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(
        max_length=53,
        help_text="What would you like to offer to sell? (50 characters maximum)",
    )
    description = models.TextField(
        max_length=540,
        help_text="How would you descibe your item? (500 characters maximum)",
    )
    image = models.ImageField(
        upload_to="images/",
        help_text="Do you have a photo of your item?",
        blank=True,
    )
    price = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(100000),
            MinValueValidator(1),
        ],
        help_text="What would you like to start the item price at (Whole dollars only, maximum of 100000)",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="listings",
        help_text="Who are you?",
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="listings",
        help_text="Which category best describes your item?",
    )
    active = models.BooleanField(
        default=True, help_text="Is this item still eavailable?"
    )
    completed = models.BooleanField(default=False, help_text="Was this item sold?")
    watchers = models.ManyToManyField(
        User,
        related_name="watching",
        help_text="Relationship between users and listings",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When was this item listing created?",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When was this item listing last updated?",
    )

    def __str__(self):
        return f"{self.id} - {self.title} (Active: {self.active})"  # type: ignore


class Bid(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bids",
        help_text="Related listing",
    )
    price = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(100000),
            MinValueValidator(1),
        ],
        help_text="Bid price",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids",
        help_text="Related user",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Bid creation time",
    )

    def __str__(self):
        return f"{self.user} @ {self.price}"


class Comment(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Related listing",
    )
    text = models.TextField(
        help_text="Comment text",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Related user",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Comment creation time",
    )

    def __str__(self):
        return f"{self.user} ({self.created_at}): {self.text}"


class Category(models.Model):
    name = models.CharField(
        max_length=200,
        help_text="Category name",
    )
    icon = models.CharField(
        max_length=50,
        help_text="An icon representing the category from the list of available Bootstrap icons",
    )
    description = models.TextField(
        help_text="Description of the category",
    )
    hex_color_code = models.CharField(
        max_length=6,
        help_text="The 6 digit hex color code for the category background (https://htmlcolorcodes.com/)",
    )

    def __str__(self):
        return self.name
