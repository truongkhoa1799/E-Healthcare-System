import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras

output_saved_model_dir = '/home/thesis/Documents/thesis/E-Healthcare-System/model_engine/tf_mask_detector_model_trt'
input_saved_model_dir = '/home/thesis/Documents/thesis/E-Healthcare-System/model_engine/tf_mask_detector_model'

# model = tf.keras.models.load_model(output_saved_model_dir)
# img_path = '/home/thesis/Documents/thesis/mask_data/mask/0.jpg'
# class_names = ['mask', 'unmask']

model = tf.saved_model.load(output_saved_model_dir)

img = cv2.imread(img_path)
img = cv2.resize(img,(100, 150))

img_array = keras.preprocessing.image.img_to_array(img)
img_array = tf.expand_dims(img_array, 0) # Create a batch

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])

print(
    "This image most likely belongs to {} with a {:.2f} percent confidence."
    .format(class_names[np.argmax(score)], 100 * np.max(score))
)

# from tensorflow.python.compiler.tensorrt import trt_convert as trt

# # Conversion Parameters 
# conversion_params = trt.TrtConversionParams(
#     precision_mode=trt.TrtPrecisionMode. FP16)

# converter = trt.TrtGraphConverterV2(
#     input_saved_model_dir=input_saved_model_dir,
#     conversion_params=conversion_params)

# # Converter method used to partition and optimize TensorRT compatible segments
# converter.convert()

# # Save the model to the disk 
# converter.save(output_saved_model_dir)

