import os
import numpy as np
from models.Resnet import InceptionResNetV1

WEIGHT_BASE = os.path.join(
    os.getcwd(),"weights","model_weights_facenet")


def load_model():
    # load model from source
    model = InceptionResNetV1()

    # Load weights layer by layer
    layer_files = os.listdir(WEIGHT_BASE)
    for i, layer in enumerate(model.layers):
        weight_files = [x for x in layer_files if x.split(".")[
            0] == layer.name]
        for weight_file in weight_files:
            files_loaded = np.load(os.path.join(WEIGHT_BASE, weight_file))
            weights_for_layer = []
            for file in files_loaded:
                weights_for_layer.append(files_loaded[file])
        try:
            layer.set_weights(weights_for_layer)
        except:
            pass

    return model

