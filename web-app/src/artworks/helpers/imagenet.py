import os
import numpy as np

from joblib import load
from PIL import Image as pil_image
from numpy import linalg as LA
from sklearn.decomposition import PCA

from django.conf import settings

class ImageNetWrapper:
    def __init__(self):
        from keras.models import Model
        from keras.applications.vgg16 import VGG16

        model_vgg16_conv = VGG16(weights='imagenet', pooling='max', include_top=True)

        # create new model that uses the input and the last fully connected layer from vgg16
        self.model = Model(inputs=model_vgg16_conv.input,
                outputs=model_vgg16_conv.get_layer('fc2').output)

        pca_path = os.path.join(settings.MODELS_ROOT, 'pca')
        if os.path.exists(pca_path):
            self.pca = load(pca_path)

        scaler_path = os.path.join(settings.MODELS_ROOT, 'scaler')
        if os.path.exists(scaler_path):
            self.scaler = load(scaler_path)


    def predict(self, artwork, train=False):
        from keras.preprocessing import image
        from keras.applications.vgg16 import preprocess_input

        #create placeholder for images to go through neural net
        images = np.zeros(shape=(1, 224, 224, 3))

        #Keras is more used to deal with PIL images 
        img = pil_image.open(artwork)
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
        vector = self.model.predict(inputs)
        # vector = np.array([vector[0] / LA.norm(vector[0])])

        if train:
            return vector

        scaled_vector = self.scaler.transform(vector)
        return self.pca.transform(scaled_vector)
                