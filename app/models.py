import tensorflow as tf
import pickle
import numpy as np

# Load the ML model
MODEL_PATH = r'D:\AI Fashion Wadrobe Project\Backend\app\models\Fashion_attribute_prediction_model\resnet_based.keras'
LABEL_BINARIZER_PATH = r'D:\AI Fashion Wadrobe Project\Backend\app\models\Fashion_attribute_prediction_model\label_binarizers.pkl'

model = tf.keras.models.load_model(MODEL_PATH)

# Load the label binarizers
with open(LABEL_BINARIZER_PATH, "rb") as file:
    LB = pickle.load(file)

# Prediction labels
labels = ['gender', 'masterCategory', 'subCategory', 'articleType', 'season', 'usage']

def predict_attributes(image_array):
    """Predicts attributes for the given image array."""
    processed_image = np.expand_dims(image_array, axis=0)
    output_probs = model.predict(processed_image, verbose=0)

    predicted_classes = {}
    for i, probs in enumerate(output_probs):
        out = LB[labels[i]].inverse_transform(np.array(probs == probs.max(), dtype=np.int64))
        predicted_classes[labels[i]] = str(out[0])
    
    return predicted_classes
