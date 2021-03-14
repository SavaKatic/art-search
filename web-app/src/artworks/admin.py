from django.contrib import admin

from src.artworks.models import Artwork, Artist

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    search_fields = ('title',)
