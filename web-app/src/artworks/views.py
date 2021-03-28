from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from src.artworks.apps import ArtworksConfig

# Create your views here.


class SearchArtworkView(APIView):
    """
        Search artwork database view.
    """

    parser_classes = (MultiPartParser, FormParser, )

    def post(self, request):
        """
            API endpoint that allows user to search for artwork.
        """

        image = request.data.get('artwork', None)
        if not image:
            return Response({'error': 'Image was not passed in request body.'}, status=status.HTTP_400_BAD_REQUEST)

        vector = ArtworksConfig.searcher.predict(image)

        data = ArtworksConfig.es.semantic_search(vector)
        return Response(data=data, status=status.HTTP_200_OK)
