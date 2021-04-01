# Art Search

An AR artwork search application implemented in Keras, Django, ElasticSearch and Unity.

## Setup
To install all the dependencies, run following command:
```
pip install -r requirements.txt
```

## Problem

You are in a gallery and would like to have additional visual data about art pieces you see. With an application like this, you can search the database of artworks with a single tap on the screen and additional info like artwork name, description, price will pop up.

## Solution

The system can be separated into two modules:
* Unity Client application - provides search indicator that is placed flat on a plane. Once the user taps on the screen a screenshot is made that is sent to the API server. When API gives back the result it is displayed in 3D. Whole process can be repeated again.
* Django Backend - provides a search endpoint that takes in an image (screenshot from AR application). It creates a vector representation of the image using VGG16 neural network and PCA to reduce dimensionality of this vector. The vector is later used to query data in ElasticSearch using cosine similarity, which gives the most similar image from the database and its basic information.

## Demo

![DEMO](./assets/demo.gif)

### Author: Sava Katic
