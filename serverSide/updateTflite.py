
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D

# Custom loading workaround to ignore unrecognized args like 'groups'
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        kwargs.pop('groups', None)  # Strip out 'groups' if present
        super().__init__(*args, **kwargs)

# Use custom object scope
model = load_model("model.h5", custom_objects={'CustomDepthwiseConv2D': CustomDepthwiseConv2D})

train_dataset = tf.keras.utils.image_dataset_from_directory(
    "extracted",                 # root directory path
    image_size=(224, 224),  # resize all images to this size
    batch_size=32,          # how many images per training batch
    label_mode='int',       # 'int', 'categorical', or 'binary'
    shuffle=True
)

normalization_layer = tf.keras.layers.Rescaling(1./255)

train_dataset = train_dataset.map(lambda x, y: (normalization_layer(x), y))

for images, labels in train_dataset.take(1):
    print(images.shape)  # (batch_size, 224, 224, 3)
    print(labels.numpy())  # e.g., [0, 1, 1, 0, ...]

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train_dataset, epochs = 5)

model.save("model.h5")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
num = 0
with open("savedModels/count.txt", "r") as file:
    content = file.read()
    try:
        num = int(content.strip())
    except ValueError:
        num = 0

with open("model.tflite", "wb") as f:
    f.write(tflite_model)

with open("savedModels/model" + str(num) + ".tflite", "wb") as f:
    f.write(tflite_model)

num += 1

with open("savedModels/count.txt", "w") as file:
    file.write(str(num))


with open("savedNonTfliteModels/count.txt", "r") as file:
    content = file.read()
    try:
        num = int(content.strip())
    except ValueError:
        num = 0

model.save("savedNonTfliteModels/model" + str(num) + ".h5")

num += 1

with open("savedNonTfliteModels/count.txt", "w") as file:
    file.write(str(num))


