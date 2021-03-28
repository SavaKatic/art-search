from django.conf.urls import url

from src.artworks.views import SearchArtworkView


urlpatterns = [
    url('search-artworks/', SearchArtworkView.as_view(), name='search-artworks')
]
