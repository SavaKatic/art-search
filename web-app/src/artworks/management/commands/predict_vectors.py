import os
import numpy as np

from keras.preprocessing import image
from keras.models import Model
from keras.applications.vgg16 import VGG16, preprocess_input
from PIL import Image as pil_image

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
        model_vgg16_conv = VGG16(weights='imagenet', include_top=True)

        # create new model that uses the input and the last fully connected layer from vgg16
        model = Model(inputs=model_vgg16_conv.input,
                outputs=model_vgg16_conv.get_layer('fc2').output)

        qs = Artwork.objects.filter(image__isnull=False)
        fetcher = self.lazy_bulk_fetch(1000, qs.count(), lambda: qs.all())

        # create ES connection
        es = ElasticConnector(settings.ES_HOST, settings.ES_PORT)

        for batch in fetcher:
            for artwork in batch:
                #create placeholder for images to go through neural net
                print(f"Artwork: {artwork.title} ")
                images = np.zeros(shape=(1, 224, 224, 3))

                #Keras is more used to deal with PIL images 
                img = pil_image.open(artwork.image.path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Model requires the input shape to be (224,224,3)    
                img = img.resize((224, 224), pil_image.NEAREST)
                x_raw = image.img_to_array(img)

                #overwrite first instance of images placeholder with the image array
                x_expand = np.expand_dims(x_raw, axis=0)
                images[0, :, :, :] = x_expand

                # preprocess your image to be able to enter the neural network
                inputs = preprocess_input(images)

                #predict image features
                images_features = model.predict(inputs)
                vector = images_features[0]
                
                # save data into ES
                es.insert_artwork({
                    'title': artwork.title,
                    'description': artwork.description,
                    'img_vec': vector,
                    'artwork_id': artwork.id
                })
