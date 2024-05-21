# -*- coding: utf-8 -*-
"""Final_comparisionModelPlantDisease.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EqeOWSrfGxCPa4noey1yw0FmgRpER25T

### **1. Plant Disease Detection**
"""

from google.colab import drive
drive.mount('/content/drive')

from tensorflow.python.client import device_lib
device_lib.list_local_devices()

# Commented out IPython magic to ensure Python compatibility.
#Adding DataBase to drive
# %pwd
!cp -r /content/drive/MyDrive/Dataset /content

"""#### **1.1. Import Required Libraries**


"""

import os
import cv2
import glob
import datetime
import pandas as pd
import numpy as np
import keras
import tensorflow as tf
import matplotlib.pyplot as plt
from keras.layers import Dense
from keras.models import Sequential
import keras.utils as image
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Model
from keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.vgg19 import VGG19
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input
from keras.layers import Convolution2D,Dense,MaxPool2D,Activation,Dropout,Flatten
from keras.layers import Input, Add, Dense, Activation, ZeroPadding2D, BatchNormalization, Flatten, Conv2D, AveragePooling2D, MaxPooling2D, GlobalMaxPooling2D

"""#### **1.2. Test-Train Data**
**Split the dataset**

**os.walk()-->**This function gives the possibility to list the contents of a directory. For example, it is used to find out which files and subdirectories are in the current directory.
"""

def get_files(directory):
  if not os.path.exists(directory):
    return 0
  count=0
  # crawls inside folders
  for current_path,dirs,files in os.walk(directory):
    for dr in dirs:
      count+= len(glob.glob(os.path.join(current_path,dr+"/*")))
  return count
train_dir ="/content/Dataset/Train "
test_dir="/content/Dataset/Test"

"""**glob.glob()-->**It is a module that helps to list files in a specific folder in Python. Searches in subfolders."""

#train file image count
train_samples =get_files(train_dir)
#to get tags
num_classes=len(glob.glob(train_dir+"/*"))
#test file image count
test_samples=get_files(test_dir)
print(num_classes,"Classes")
print(train_samples,"Train images")
print(test_samples,"Test images")

"""#### **1.3. ImageDataGenerator**

**ImageDataGenerator**,Data augmentation is used to increase the size of training set and to get more different image. Through Data augmentation we can prevent overfitting ,this refers to randomly changing the images in ways that shouldn’t impact their interpretation, such as horizontal flipping, zooming, and rotating
* **Rescale:** One of the many magnification parameters adjusts the pixel values of our image.
* **Shear_range:** counterclockwise shear angle in degrees
* **Zoom_range:** zoom
* **Horizontal_flip:** flip image horizontally
"""

train_datagen=ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
    )
test_datagen=ImageDataGenerator(rescale=1./255)

"""**flow_from_directory() -->** Another method to read images into TensorFlow environment is to use the .flow_from_directory() method. flow_from_directory is an ImageDataGenerator method. The dataset is read with flow_from_directory without making any changes.

**Parameters:**
* **directory:** The path of the target directory. It must contain one subdirectory per class. Any PNG, JPG, BMP, PPM or TIF formatted images found in each of the subdirectories will be included in the generator.
* **target_size:** A tuple of integers, (height, width), by default (256,256). All found images will be resized.
* **batch_size:** The size of the data chunks (default: 32).
* **shuffle:** Decides whether to shuffle data (default: True). If set to false, it sorts the data in alphanumeric order.


"""

input_shape=(224,224,3)
train_generator =train_datagen.flow_from_directory(train_dir,target_size=(224,224),batch_size=32)
test_generator=test_datagen.flow_from_directory(test_dir,shuffle=True,target_size=(224,224),batch_size=32)

#install TensorFlow 2.0
!pip install tensorflow==2.0.0-alpha0

"""#### **1.4. CNN Model**

A Convolutional Neural Network (ConvNet/CNN) is a Deep Learning algorithm which can take in an input image, assign importance (learnable weights and biases) to various aspects/objects in the image and be able to differentiate one from the other. The pre-processing required in a ConvNet is much lower as compared to other classification algorithms. While in primitive methods filters are hand-engineered, with enough training, ConvNets have the ability to learn these filters/characteristics.
"""

model = Sequential()
model.add(Conv2D(32, (5, 5),input_shape=input_shape,activation='relu',name="conv2d_1"))
model.add(MaxPooling2D(pool_size=(3, 3),name="max_pooling2d_1"))
model.add(Conv2D(32, (3, 3),activation='relu',name="conv2d_2"))
model.add(MaxPooling2D(pool_size=(2, 2),name="max_pooling2d_2"))
model.add(Conv2D(64, (3, 3),activation='relu',name="conv2d_3"))
model.add(MaxPooling2D(pool_size=(2, 2),name="max_pooling2d_3"))
model.add(Flatten(name="flatten_1"))
model.add(Dense(512,activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(128,activation='relu'))
model.add(Dense(num_classes,activation='softmax'))
model.summary()

validation_generator = train_datagen.flow_from_directory(
                       test_dir,
                       target_size=(224, 224),
                       batch_size=32)

from tensorflow.keras.utils import plot_model
plot_model(model)

"""When compiling the model, we provide **objective function (loss)**, **optimization method (adam)** and **accuracy** that we will follow.

For training, the 'fit()' function is used in the model with the following parameter:
* **train:** training data,
* **validation_data:** validation set,
* **shuffle:** change of location of data in each epoch,
* **verbose:** to be able to see the outputs during the training (0-> does not show, 1-> does)
* **epoch:** determines how many times the dataset will be trained by traversing the model
* **callbacks:** An object that can perform actions at various stages of training (for example, at the beginning or end of a period, before or after a single batch, etc.).

**ReduceLROnPlateau():** Models benefit from reducing the learning rate by 2-10 times when learning becomes sluggish. If it checks and no improvement is seen for the 'patience' count, the learning rate drops.
* **monitor**: value to monitor
* **factor:** factor by which the learning rate will be reduced
* **patience**: the number of non-development periods after which the learning rate will decrease
* **min_lr:** lower limit of learning rate
"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir logs

Epoch = 5 #@param {type:"number"}
Patience =3 #@param {type:"number"}

model.compile(optimizer='adam',loss = 'categorical_crossentropy',metrics=['accuracy'])
logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)
history1 = model.fit(
    train_generator,
    steps_per_epoch=None,
    epochs=Epoch,
    validation_data=validation_generator,
    validation_steps=None,
    verbose=1,
    callbacks=[ReduceLROnPlateau(monitor='val_loss', factor=0.3,patience=Patience, min_lr=0.000001),tensorboard_callback],
    shuffle=True
    )

model.save('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_Cnn.h5')

"""#### **1.5. VGG16 Model**

**VGG16** Architecture consists of 16 layers.

* **include_top :** Whether to include 3 layers fully connected to the top of the network
* **weight:** checkpoint from which model is initialized
"""

def create_Base_model_from_VGG16():
    model = VGG16(
        weights = "imagenet",
        include_top=False,
        input_shape = (224,224, 3)
        )
    for layer in model.layers:
      layer.trainable = False
    return model
create_Base_model_from_VGG16().summary()

def add_custom_layers():
    model = create_Base_model_from_VGG16()
    x = model.output
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    predictions = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    # creating the final model
    final_model = tf.keras.models.Model(
        inputs = model.input,
        outputs = predictions)

    final_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return final_model

add_custom_layers().summary()

validation_generator = train_datagen.flow_from_directory(
                       test_dir, # same directory as training data
                       target_size=(224, 224),
                       batch_size=32)

from tensorflow.keras.utils import plot_model
model_from_vgg16 = add_custom_layers()
plot_model(model_from_vgg16)

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir logs

Epoch=5 #@param {type:"number"}

logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)
history2 = model_from_vgg16.fit(
    train_generator,
    steps_per_epoch=None,
    epochs=Epoch,
    validation_data=validation_generator,
    validation_steps=None,
    verbose=1,
    callbacks=[ReduceLROnPlateau(monitor='val_loss', factor=0.3,patience=3, min_lr=0.000001),tensorboard_callback],
    use_multiprocessing=False,
    shuffle=True
    )

model_from_vgg16.save('/content/drive/MyDrive/Colab Notebooks/Model/model_VGG16.h5')

"""#### **1.6. VGG19 Model**"""

def create_Base_model_from_VGG19():
    model_vgg19 = VGG19(
        weights = "imagenet",# control point from which model is started
        include_top=False, # to include/exclude the first 3 layers
        input_shape = (224,224, 3)) # image size
    # don't train existing weights
    for layer in model_vgg19.layers:
      layer.trainable = False
    return model_vgg19
create_Base_model_from_VGG19().summary()

def add_custom_layers_vgg19():
    #Adding custom Layers
    model_vgg19 = create_Base_model_from_VGG19()
    x = model_vgg19.output
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    predictions = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    # creating the final model
    final_model = tf.keras.models.Model(
        inputs = model_vgg19.input,
        outputs = predictions)

    final_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return final_model

add_custom_layers_vgg19().summary()

validation_generator = train_datagen.flow_from_directory(
                       test_dir,
                       target_size=(224, 224),
                       batch_size=32)

from tensorflow.keras.utils import plot_model
model_from_vgg19 = add_custom_layers_vgg19()
plot_model(model_from_vgg19)

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir logs

logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)
history3 = model_from_vgg19.fit(train_generator,
                      steps_per_epoch=None,
                      epochs=5,
                      validation_data=validation_generator,
                      validation_steps=None,
                      verbose=1,
                      callbacks=[ReduceLROnPlateau(monitor='val_loss', factor=0.3,patience=3, min_lr=0.000001),tensorboard_callback],
                      use_multiprocessing=False,
                      shuffle=True)

model_from_vgg19.save('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_VGG19.h5')

"""#### **1.7. InceptionV3 Model**

The model will be downloaded automatically the first time the command is run to create the model. Assigning the weight parameter to the imagenet will enable the weights of the imagenet model to be used. If we want to train something using the Inception mesh, the weight parameter can be set to None, that way the weights will be randomly generated with default values.
"""

IMAGE_SIZE = [224, 224]
inception = InceptionV3(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)
# We don't need to train existing weights
for layer in inception.layers:
    layer.trainable = False

# Model layers -> can add more if required
x = Flatten()(inception.output)
prediction = Dense(num_classes, activation='softmax')(x)
# Create a model object
model = Model(inputs=inception.input, outputs=prediction)
# View the structure of the model
model.summary()

validation_generator = train_datagen.flow_from_directory(
                       test_dir,
                       target_size=(224, 224),
                       batch_size=32)

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir logs

# Defining the cost and model optimization method to use
model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)
history4 = model.fit(
    train_generator,
    steps_per_epoch=None,
    epochs=5,
    validation_data=validation_generator,
    validation_steps=None,
    verbose=1,
    callbacks=[ReduceLROnPlateau(monitor='val_loss', factor=0.3,patience=3, min_lr=0.000001),tensorboard_callback],
    shuffle=True)

# Saving the model as a h5 file
model.save('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_inception.h5')

"""#### **1.8. AlexNet**

This deep convolutional neural network consisting of 25 layers consists of 5 convolution layers, 3 maxpool layers, 2 dropout layers, 3 fully connected layers, 7 relu layers, 2 normalization layers, softmax layer, input and classification (output) layers. .
"""

# Importing Keras libraries and packages
from keras.models import Sequential
from keras.layers import Convolution2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import BatchNormalization

# Initializing the CNN
model = Sequential()
# Convolution Step 1
model.add(Convolution2D(96, 11, strides = (4, 4), padding = 'valid', input_shape=(224, 224, 3), activation = 'relu'))
# Max Pooling Step 1
model.add(MaxPooling2D(pool_size = (2, 2), strides = (2, 2), padding = 'valid'))
model.add(BatchNormalization())
# Convolution Step 2
model.add(Convolution2D(256, 11, strides = (1, 1), padding='valid', activation = 'relu'))
# Max Pooling Step 2
model.add(MaxPooling2D(pool_size = (2, 2), strides = (2, 2), padding='valid'))
model.add(BatchNormalization())
# Convolution Step 3
model.add(Convolution2D(384, 3, strides = (1, 1), padding='valid', activation = 'relu'))
model.add(BatchNormalization())
# Convolution Step 4
model.add(Convolution2D(384, 3, strides = (1, 1), padding='valid', activation = 'relu'))
model.add(BatchNormalization())
# Convolution Step 5
model.add(Convolution2D(256, 3, strides=(1,1), padding='valid', activation = 'relu'))
# Max Pooling Step 3
model.add(MaxPooling2D(pool_size = (2, 2), strides = (2, 2), padding = 'valid'))
model.add(BatchNormalization())
# Flattening Step
model.add(Flatten())
# Full Connection Step
model.add(Dense(units = 4096, activation = 'relu'))
model.add(Dropout(0.4))
model.add(BatchNormalization())
model.add(Dense(units = 4096, activation = 'relu'))
model.add(Dropout(0.4))
model.add(BatchNormalization())
model.add(Dense(units = 1000, activation = 'relu'))
model.add(Dropout(0.2))
model.add(BatchNormalization())
model.add(Dense(units = num_classes, activation = 'softmax'))
model.summary()

validation_generator = train_datagen.flow_from_directory(
                       test_dir,
                       target_size=(224, 224),
                       batch_size=32)

from tensorflow.keras.utils import plot_model
model_from_vgg19 = add_custom_layers_vgg19()
plot_model(model)

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir logs

model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)
history = model.fit(
    train_generator,
    steps_per_epoch=None,
    epochs=15,
    validation_data=validation_generator,
    validation_steps=4,
    verbose=1,
    callbacks=[ReduceLROnPlateau(monitor='val_loss', factor=0.3,patience=3, min_lr=0.000001),tensorboard_callback],
    shuffle=True)

model.save('/content/drive/MyDrive/Colab Notebooks/MyModels/model__Alexnet.h5')

print("[INFO] Calculating model accuracy")
scores = model.evaluate(validation_generator)
print(f"Test Accuracy: {scores[1]*100}")

results = model.evaluate(test_generator, verbose=1)

print("    Test Loss: {:.5f}".format(results[0]))
print("Test Accuracy: {:.2f}%".format(results[1] * 100))

# Predict the label of the test_gen
pred = model.predict(test_generator,verbose=1)
pred = np.argmax(pred,axis=1)

# Map the label
labels = (train_generator.class_indices)
labels = dict((v,k) for k,v in labels.items())
pred = [labels[k] for k in pred]

import sklearn.metrics
y_test = list(train_generator.labels)
print(sklearn.metrics.classification_report(y_test[:6052], pred))

from keras.models import Sequential
from keras.layers import Dense
import matplotlib.pyplot as plt
import numpy

print(history5.history.keys())

plt.plot(history5.history['accuracy'])
plt.plot(history5.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history5.history['loss'])
plt.plot(history5.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""#### **1.9. ResNet50 Model**"""

pretrained_model = tf.keras.applications.resnet50.ResNet50(
    input_shape=(224,224, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg'
)
pretrained_model.trainable = False

inputs = pretrained_model.input

x = Dense(128, activation='relu')(pretrained_model.output)
x = Dense(128, activation='relu')(x)

outputs = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=inputs, outputs=outputs)

pretrained_model.summary()

model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
my_callbacks  = [tf.keras.callbacks.EarlyStopping(monitor='val_loss',min_delta=0,patience=3,mode='auto')]

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir logs

from tensorflow.keras.utils import plot_model
plot_model(model)

logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)
history = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=10,
    callbacks=[my_callbacks,tensorboard_callback],
    verbose=1,
    steps_per_epoch=None,
    validation_steps=4
)

model.save('/content/drive/MyDrive/Colab Notebooks/MyModels/model_resnet50.h5')

print("[INFO] Calculating model accuracy")
scores = model.evaluate(validation_generator)
print(f"Test Accuracy: {scores[1]*100}")

pd.DataFrame(history.history)[['accuracy','val_accuracy']].plot()
plt.title("Accuracy")
plt.show()

pd.DataFrame(history.history)[['loss','val_loss']].plot()
plt.title("Loss")
plt.show()

"""### **2. Prediction From the model**

#### **2.1. CNN Model**
"""

import numpy as np
from keras.models import load_model
from keras.preprocessing import image
model_cnn=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_Cnn.h5')

classes=list(train_generator.class_indices.keys())
# Pre-Processing test data same as train data.
def prepare(img_path):
    img = keras.utils.load_img(img_path, target_size=(224,224))
    x = tf.keras.utils.img_to_array(img)
    x = x/255
    return np.expand_dims(x, axis=0)

img_url='/content/Dataset/Test/Soybean___healthy/077906a4-255c-4330-9fb6-e923f58ae1d4___RS_HL 3890.JPG'
result_cnn = model_cnn.predict([prepare(img_url)])
disease=keras.utils.load_img(img_url)
plt.imshow(disease)

classresult=np.argmax(result_cnn,axis=1)
print(classes[classresult[0]])

tot=0
curr=0
import os
dir = '/content/Dataset/Test'
for f1 in os.scandir(dir):
  for f2 in os.listdir(f1):
    tot = tot+1
    strin = str(f1)
    img_dir = os.path.join(dir,f1,f2)
    curr_res = model_cnn.predict([prepare(img_dir)])
    disease = keras.utils.load_img(img_dir)
    plt.imshow(disease)
    classresult = np.argmax(curr_res,axis=1)
    res = strin.split("'")
    print(classes[classresult[0]],curr)
    if(classes[classresult[0]]==res[1]):
      curr=curr+1;

os.system('cls')
print("accuracy on test dataset = ", curr/tot*100)

"""#### **2.2. VGG16 Model**"""

import numpy as np
from keras.models import load_model
from keras.preprocessing import image
model_vgg16=load_model('/content/drive/MyDrive/Colab Notebooks/Model/model_VGG16.h5')

classes=list(train_generator.class_indices.keys())
# Pre-Processing test data same as train data.
def prepare(img_path):
    img = keras.utils.load_img(img_path, target_size=(224,224))
    x = tf.keras.utils.img_to_array(img)
    x = x/255
    return np.expand_dims(x, axis=0)

img_url='/content/Dataset/Test/Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot/ce3b19bd-dace-4d23-836e-233b02f12300___RS_GLSp 4505.JPG'
result_vgg16 = model_vgg16.predict([prepare(img_url)])
disease=keras.utils.load_img(img_url)
plt.imshow(disease)

classresult=np.argmax(result_vgg16,axis=1)
print(classes[classresult[0]])

tot=0
curr=0
import os
dir = '/content/Dataset/Test'
for f1 in os.scandir(dir):
  for f2 in os.listdir(f1)[:10]:
    tot = tot+1
    strin = str(f1)
    img_dir = os.path.join(dir,f1,f2)
    curr_res = model_vgg16.predict([prepare(img_dir)])
    disease = keras.utils.load_img(img_dir)
    plt.imshow(disease)
    classresult = np.argmax(curr_res,axis=1)
    res = strin.split("'")
    print(classes[classresult[0]],curr)
    if(classes[classresult[0]]==res[1]):
      curr=curr+1;

os.system('cls')
print("accuracy on test dataset = ", curr/tot*100)

"""#### **2.3. VGG19 Model**"""

import numpy as np
from keras.models import load_model
from keras.preprocessing import image
model_vgg19=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_VGG19.h5')

classes=list(train_generator.class_indices.keys())
# Pre-Processing test data same as train data.
def prepare(img_path):
    img = keras.utils.load_img(img_path, target_size=(224,224))
    x = tf.keras.utils.img_to_array(img)
    x = x/255
    return np.expand_dims(x, axis=0)

img_url='/content/Dataset/Test/Orange___Haunglongbing_(Citrus_greening)/cd0611a2-82eb-48f5-99b2-c2801d9d8eeb___CREC_HLB 7775.JPG'
result_vgg19 = model_vgg19.predict([prepare(img_url)])
disease=keras.utils.load_img(img_url)
plt.imshow(disease)

classresult=np.argmax(result_vgg19,axis=1)
print(classes[classresult[0]])

"""#### **2.4. Inception Model**"""

import numpy as np
from keras.models import load_model
from keras.preprocessing import image
model_inception=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_inception.h5')

classes=list(train_generator.class_indices.keys())
# Pre-Processing test data same as train data.
def prepare(img_path):
    img = keras.utils.load_img(img_path, target_size=(224,224))
    x = tf.keras.utils.img_to_array(img)
    x = x/255
    return np.expand_dims(x, axis=0)

img_url='/content/Dataset/Test/Potato___Early_blight/cff1ed1b-51ec-4d44-ab1f-7a3dc1ec9ea9___RS_Early.B 7100.JPG'
result_inception = model_inception.predict([prepare(img_url)])
disease=keras.utils.load_img(img_url)
plt.imshow(disease)

classresult=np.argmax(result_inception,axis=1)
print(classes[classresult[0]])

"""#### **2.5. AlexNet Model**"""

import numpy as np
from keras.models import load_model
from keras.preprocessing import image
model_alexnet=load_model('/content/drive/MyDrive/Colab Notebooks/MyModels/model__Alexnet.h5')

classes=list(train_generator.class_indices.keys())
# Pre-Processing test data same as train data.
def prepare(img_path):
    img = keras.utils.load_img(img_path, target_size=(224,224))
    x = tf.keras.utils.img_to_array(img)
    x = x/255
    return np.expand_dims(x, axis=0)

img_url='/content/Dataset/Test/Corn_(maize)___Northern_Leaf_Blight/d0aa3b59-046b-490d-a333-8049b87d5db9___RS_NLB 4147 copy.jpg'
result_alexnet = model_alexnet.predict([prepare(img_url)])
disease=keras.utils.load_img(img_url)
plt.imshow(disease)

classresult=np.argmax(result_alexnet,axis=1)
print(classes[classresult[0]])

"""#### **2.6. ResNet50 Model**"""

import numpy as np
from keras.models import load_model
from keras.preprocessing import image
model_alexnet=load_model('/content/drive/MyDrive/Colab Notebooks/MyModels/model_resnet50.h5')

classes=list(train_generator.class_indices.keys())
# Pre-Processing test data same as train data.
def prepare(img_path):
    img = keras.utils.load_img(img_path, target_size=(224,224))
    x = tf.keras.utils.img_to_array(img)
    x = x/255
    return np.expand_dims(x, axis=0)

img_url='/content/Dataset/Test/Raspberry___healthy/cfa94853-c6b9-4f40-a8ae-9120269066c4___Mary_HL 9182.JPG'
result_alexnet = model_alexnet.predict([prepare(img_url)])
disease=keras.utils.load_img(img_url)
plt.imshow(disease)

classresult=np.argmax(result_alexnet,axis=1)
print(classes[classresult[0]])

"""#### **2.7. All Model**"""

def prepare(img_path):
    img = keras.utils.load_img(img_path, target_size=(224,224))
    x = tf.keras.utils.img_to_array(img)
    x = x/255
    return np.expand_dims(x, axis=0)

def predict_all(img_dir):
  model_cnn=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_Cnn.h5')
  model_vgg16=load_model('/content/drive/MyDrive/Colab Notebooks/Model/model_VGG16.h5')
  model_vgg19=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_VGG19.h5')
  model_inception=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_inception.h5')
  model_alexnet=load_model('/content/drive/MyDrive/Colab Notebooks/MyModels/model__Alexnet.h5')
  model_restnet50=load_model('/content/drive/MyDrive/Colab Notebooks/MyModels/model_resnet50.h5')
  img_url= img_dir
  classes=list(train_generator.class_indices.keys())
  #cnn
  result_cnn = model_cnn.predict([prepare(img_url)])
  disease=keras.utils.load_img(img_url)
  classresult_cnn=np.argmax(result_cnn,axis=1)
  print("CNN_Model Prediction -> ", classes[classresult_cnn[0]])

  #vgg16
  result_vgg16 = model_vgg16.predict([prepare(img_url)])
  disease=keras.utils.load_img(img_url)
  classresult_vgg16=np.argmax(result_vgg16,axis=1)
  print("VGG16 Prediction -> ", classes[classresult_vgg16[0]])

  #vgg19
  result_vgg19 = model_vgg19.predict([prepare(img_url)])
  disease=keras.utils.load_img(img_url)
  classresult_vgg19=np.argmax(result_vgg19,axis=1)
  print("VGG19 Prediction -> ", classes[classresult_vgg19[0]])

  #incep
  result_incep = model_inception.predict([prepare(img_url)])
  disease=keras.utils.load_img(img_url)
  classresult_incep=np.argmax(result_incep,axis=1)
  print("Incep Prediction -> ", classes[classresult_incep[0]])

  #resnet
  result_restnet = model_restnet50.predict(prepare(img_url))
  disease=keras.utils.load_img(img_url)
  classresult_restnet = np.argmax(result_restnet,axis =1)
  print("RestNet Prediction ->", classes[classresult_restnet[0]])

  #alexnet
  result_alex = model_alexnet.predict(prepare(img_url))
  disease=keras.utils.load_img(img_url)
  classresult_alex = np.argmax(result_alex,axis =1)
  print("AlexNet Prediction ->", classes[classresult_alex[0]])

predict_all('/content/Dataset/Test/Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot/ce3b19bd-dace-4d23-836e-233b02f12300___RS_GLSp 4505.JPG')

"""#### **2.8. Temp**"""

#Plot the confusion matrix. Set Normalize = True/False
def plot_confusion_matrix(cm, classes, normalize=True, title='Confusion matrix', cmap=plt.cm.Blues):
  """
  This function prints and plots the confusion matrix.
  Normalization can be applied by setting `normalize=True`.
  """
  plt.figure(figsize=(20,20))
  plt.imshow(cm, interpolation='nearest', cmap=cmap)
  plt.title(title)
  plt.colorbar()
  tick_marks = np.arange(len(classes))
  plt.xticks(tick_marks, classes, rotation=90)
  plt.yticks(tick_marks, classes)
  if normalize:
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    cm = np.around(cm, decimals=2)
    cm[np.isnan(cm)] = 0.0
    print("Normalized confusion matrix")
  else:
    print('Confusion matrix, without normalization')
  thresh = cm.max() / 2
  for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    plt.text(j, i, cm[i, j],
             horizontalalignment="center",
             color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

validation_generator = train_datagen.flow_from_directory(
                       test_dir,
                       target_size=(224, 224),
                       batch_size=32)

#Print the Target names
from sklearn.metrics import classification_report, confusion_matrix
import itertools

#shuffle=False
target_names = []

for key in train_generator.class_indices:
    target_names.append(key)
print(target_names)

model_cnn=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_Cnn.h5')
model_vgg16=load_model('/content/drive/MyDrive/Colab Notebooks/Model/model_VGG16.h5')
model_vgg19=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_VGG19.h5')
model_inception=load_model('/content/drive/MyDrive/Colab Notebooks/Model/plant_disease_inception.h5')
model_alexnet=load_model('/content/drive/MyDrive/Colab Notebooks/MyModels/model__Alexnet.h5')
model_restnet50=load_model('/content/drive/MyDrive/Colab Notebooks/MyModels/model_resnet50.h5')

#Confution Matrix
Y_pred = model_cnn.predict_generator(train_generator)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
cm = confusion_matrix(y_pred,train_generator.classes)
plot_confusion_matrix(cm, target_names, title='Confusion Matrix')

#Print Classification Report
print('Classification Report')
print(classification_report(train_generator.classes, y_pred, target_names=target_names))

y_pred = model_cnn.predict(validation_generator)

y_pred = np.argmax(y_pred, axis=1)

y_pred

y_test = validation_generator.classes

target_names

cm = confusion_matrix(y_pred,y_test)

from sklearn.metrics import ConfusionMatrixDisplay
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_names)

disp.plot(cmap=plt.cm.Blues)
plt.show()

#Confution Matrix
Y_pred = model_vgg16.predict_generator(train_generator)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
cm = confusion_matrix(train_generator.classes, y_pred)
plot_confusion_matrix(cm, target_names, title='Confusion Matrix')

#Print Classification Report
print('Classification Report')
print(classification_report(train_generator.classes, y_pred, target_names=target_names))

#Confution Matrix
Y_pred = model_vgg19.predict_generator(validation_generator)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
cm = confusion_matrix(validation_generator.classes, y_pred)
plot_confusion_matrix(cm, target_names, title='Confusion Matrix')

#Print Classification Report
print('Classification Report')
print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

Y_pred = model_inception.predict_generator(validation_generator)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
cm = confusion_matrix(validation_generator.classes, y_pred)
plot_confusion_matrix(cm, target_names, title='Confusion Matrix')

#Print Classification Report
print('Classification Report')
print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

Y_pred = model_alexnet.predict_generator(validation_generator)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
cm = confusion_matrix(validation_generator.classes, y_pred)
plot_confusion_matrix(cm, target_names, title='Confusion Matrix')

#Print Classification Report
print('Classification Report')
print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

Y_pred = model_restnet50.predict_generator(validation_generator)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
cm = confusion_matrix(validation_generator.classes, y_pred)
plot_confusion_matrix(cm, target_names, title='Confusion Matrix')

#Print Classification Report
print('Classification Report')
print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

Y_pred = model_cnn.predict_generator(validation_generator, 6052  // 32+1)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
print(confusion_matrix(validation_generator.classes, y_pred))
print('Classification Report')
target_names
print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

