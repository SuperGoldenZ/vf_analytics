import cv2
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model

class Stage:

    def __init__(self):
        self._model = load_model('best_model.keras')


    def get_stage(self, frame):
        image_resized = cv2.resize(frame, (224,224))
        image_array = img_to_array(image_resized) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        prediction = self._model.predict(image_array)
        predicted_class_index = np.argmax(prediction[0])

        #class_labels = {v: k for k, v in class_indices.items()}

        class_labels = {0: 'Arena', 1: 'Aurora', 2: 'Broken House', 3: 'City', 4: 'Deep Mountain', 5: 'Genesis', 6:'Grassland', 
                        7:'Great Wall', 8:'Island', 9:'Palace', 10:'River', 11:'Ruins', 12:'Shrine', 13:'SnowMountain', 14:'Statues', 15:'Sumo Ring', 16:'Temple', 17:'Terrace', 18:'Training Room', 19:'Waterfals'}
        print(predicted_class_index)
        return class_labels[predicted_class_index]
