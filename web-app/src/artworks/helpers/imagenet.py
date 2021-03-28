import numpy as np

from PIL import Image as pil_image


class ImageNetWrapper:
    def __init__(self):
        from keras.models import Model
        from keras.applications.vgg16 import VGG16

        model_vgg16_conv = VGG16(weights='imagenet', include_top=True)

        # create new model that uses the input and the last fully connected layer from vgg16
        self.model = Model(inputs=model_vgg16_conv.input,
                outputs=model_vgg16_conv.get_layer('fc2').output)

        
    def predict(self, artwork):
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
        images_features = self.model.predict(inputs)
        vector = images_features[0]

        return vector
                