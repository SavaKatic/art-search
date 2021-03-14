from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from djmoney.models.fields import MoneyField

from src.common.constants import GENDER_CHOICES


class Artist(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, null=True, blank=True)
    dates = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Artwork(models.Model):
    image = ThumbnailerImageField('ArtworkImage', upload_to='artwork_images/', blank=True, null=True)
    title = models.CharField(max_length=255)
    date = models.CharField(max_length=255, null=True, blank=True)
    dimensions = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True, related_name='artworks')

    def __str__(self):
        return self.title
