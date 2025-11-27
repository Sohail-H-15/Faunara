from functools import lru_cache
from typing import Tuple

import numpy as np
from PIL import Image

from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image


@lru_cache(maxsize=1)
def _get_model() -> ResNet50:
    # Use ResNet50 without top classification layer, for feature extraction
    model = ResNet50(weights="imagenet", include_top=False, pooling="avg")
    return model


def _prepare_image(path: str) -> np.ndarray:
    img = keras_image.load_img(path, target_size=(224, 224))
    x = keras_image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x


def get_feature_vector_from_file(path: str) -> np.ndarray:
    model = _get_model()
    x = _prepare_image(path)
    features = model.predict(x)
    return features.flatten()



