# from utils.parameters import *
# import cv2
# import os, re, uuid
# import numpy as np

# from azure.iot.device import IoTHubDeviceClient
# from azure.core.exceptions import AzureError

# from identifying_users.face_recognition import Face_Recognition
# from communicate_server.server import Server
# from utils.timer import Timer
# from utils.common_functions import Compose_Embedded_Face

# ORIGINAL_DATA = '/home/thesis/Documents/E-Healthcare-System-Server/Manipulate_Data/Original_Face'
# list_name = []
# def __image_files_in_folder(folder):
#     return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

# def test_validate(user_id):
#     list_faces = ""
#     glo_va.timer = Timer()
#     glo_va.server = Server()
#     glo_va.face_recognition = Face_Recognition()
#     count = 0 
#     # for img in __image_files_in_folder(ORIGINAL_DATA + '/test/' + str(user_id)):
#     for img in __image_files_in_folder('/home/thesis/Documents/thesis/E-Healthcare-System/img_written'):
#         # glo_va.img = cv2.imread(img)

#         # ret = glo_va.face_recognition.Get_Face()
#         # if ret == -2:
#         #     print("Error Face locations")
#         #     return
#         # elif ret == 0:
#         #     # Face Identifying
#         #     print(img)
#         #     glo_va.face_recognition.Encoding_Face()
#         #     encoded_img_string = Compose_Embedded_Face(glo_va.embedded_face)
#         #     list_faces += encoded_img_string + ' '
#         count += 1
#         if count > 20:
#             break
#         glo_va.detected_face = cv2.imread(img)
#         print(img)
#         glo_va.face_recognition.Encoding_Face()
#         encoded_img_string = Compose_Embedded_Face(glo_va.embedded_face)
#         list_faces += encoded_img_string + ' '
        
#     print(len(list_faces))
#     glo_va.list_embedded_face = list_faces
#     glo_va.timer.Start_Timer(glo_va.OPT_TIMER_VALIDATE)
#     glo_va.is_sending_message = True
#     glo_va.server.Validate_User()

# test_validate(3)

# import json
# import requests

# # start_time = time.time()
# url = 'http://localhost:5005/model/parse'
# data = '{"text":"hi"}'
# response = json.loads(requests.post(url, data=data.encode('utf-8')).text)

# print(response)

import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

batch_size = 32
img_height = 100
img_width = 150

data_dir = '/home/thesis/Documents/thesis/mask_data'
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size
)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_names = train_ds.class_names
num_classes = len(class_names)
print(class_names)

AUTOTUNE = tf.data.INFINITE_CARDINALITY

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

normalization_layer = layers.experimental.preprocessing.Rescaling(1./255)

normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))
first_image = image_batch[0]
# Notice the pixels values are now in `[0,1]`.
print(np.min(first_image), np.max(first_image))

data_augmentation = keras.Sequential(
  [
    layers.experimental.preprocessing.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
    layers.experimental.preprocessing.RandomRotation(0.1),
    layers.experimental.preprocessing.RandomZoom(0.1),
  ]
)

plt.figure(figsize=(10, 10))
for images, _ in train_ds.take(1):
  for i in range(9):
    augmented_images = data_augmentation(images)
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(augmented_images[0].numpy().astype("uint8"))
    plt.axis("off")

# model = Sequential([
#   data_augmentation,
#   layers.experimental.preprocessing.Rescaling(1./255),
#   layers.Conv2D(16, 3, padding='same', activation='relu'),
#   layers.MaxPooling2D(),
#   layers.Conv2D(32, 3, padding='same', activation='relu'),
#   layers.MaxPooling2D(),
#   layers.Conv2D(64, 3, padding='same', activation='relu'),
#   layers.MaxPooling2D(),
#   layers.Dropout(0.2),
#   layers.Flatten(),
#   layers.Dense(128, activation='relu'),
#   layers.Dense(num_classes)
# ])

model = tf.keras.models.Sequential([
  data_augmentation,
  layers.experimental.preprocessing.Rescaling(1./255),
  tf.keras.layers.Flatten(input_shape=(100, 150, 3)),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(10)
])

model.compile(optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy'])

epochs = 10
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)

filepath = '/home/thesis/Documents/thesis/E-Healthcare-System/model_engine/tf_mask_detector_model'
tf.keras.models.save_model(
    model, filepath, overwrite=True, include_optimizer=True, save_format=None,
    signatures=None, options=None
)