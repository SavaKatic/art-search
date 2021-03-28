from django.apps import AppConfig
from django.conf import settings

# from src.artworks.helpers.es import ElasticConnector
# from src.artworks.helpers.imagenet import ImageNetWrapper


class ArtworksConfig(AppConfig):
    name = 'src.artworks'
    # es = ElasticConnector(settings.ES_HOST, settings.ES_PORT)
    # searcher = ImageNetWrapper()
    es = None
    searcher = None
