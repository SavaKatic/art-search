import os
import numpy as np

from keras.preprocessing import image
from keras.models import Model
from keras.applications.vgg16 import VGG16, preprocess_input
from PIL import Image as pil_image
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from joblib import dump

from django.core.management.base import BaseCommand
from django.conf import settings

from src.artworks.models import Artwork
from src.artworks.helpers.es import ElasticConnector


class Command(BaseCommand):
    def lazy_bulk_fetch(self, max_obj, max_count, fetch_func, start=0):
        counter = start
        while counter < max_count:
            yield fetch_func()[counter: counter + max_obj]
            counter += max_obj


    def handle(self, *args, **kwargs):
        from src.artworks.apps import ArtworksConfig

        qs = Artwork.objects.filter(image__isnull=False)
        fetcher = self.lazy_bulk_fetch(1000, 1024, lambda: qs.all())

        vectors = None
        for batch in fetcher:
            for artwork in batch:
                print(f"Artwork: {artwork.title} ")
                
                vector = ArtworksConfig.searcher.predict(artwork.image, train=True).tolist()
                if vectors is None:
                    vectors = np.array(vector)
                else:
                    vectors = np.append(vectors, np.array(vector), 0)
        
        print(vectors.shape)
        scaler = StandardScaler()
        scaler.fit_transform(vectors)

        pca = PCA(n_components=256)
        pca.fit_transform(vectors)

        with open(os.path.join(settings.MODELS_ROOT, 'pca'), 'wb') as f:
            dump(value=pca, filename=f)

        with open(os.path.join(settings.MODELS_ROOT, 'scaler'), 'wb') as f:
            dump(value=scaler, filename=f)

        for vector in vectors:
            scaled_vector = scaler.transform(np.array([vector]))
            reduced_dim_vector = pca.transform(scaled_vector)
            print(reduced_dim_vector)
            # save data into ES
            ArtworksConfig.es.insert_artwork({
                'title': artwork.title,
                'description': artwork.description,
                'img_vec': reduced_dim_vector[0],
                'artwork_id': artwork.id
            })
