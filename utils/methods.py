from io import BytesIO
import numpy as np
from PIL import Image
from mtcnn import MTCNN
import tensorflow as tf

def get_embedding(model, face_pixels):
    # scale pixel values
    face_pixels = face_pixels.astype('float32')

    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std

    # transform face into one sample
    samples = np.expand_dims(face_pixels, axis=0)

    samples = tf.convert_to_tensor(samples, np.float32)
    # make prediction to get embedding
    yhat = model.predict(samples)
    return yhat[0]


def extract_face(img_string, required_size=(160, 160)):

    tempBuff = BytesIO(img_string)

    # load image from file
    image = Image.open(tempBuff)
    
    # convert to array
    pixels = np.asarray(image)
    
    # create the detector, using default weights
    detector = MTCNN()
    
    # detect faces in the image
    results = detector.detect_faces(pixels)

    face_array = []
    for f in results:        
        # extract the bounding box from the first face
        x1, y1, width, height = f['box']
        # bug fix
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        
        # extract the face
        face = pixels[y1:y2, x1:x2]
    
        # resize pixels to the model size
        image = Image.fromarray(face)
        image = image.resize(required_size)
        
        face_array.append(np.asarray(image))
    return face_array
