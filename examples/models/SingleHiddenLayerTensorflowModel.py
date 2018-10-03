import tensorflow as tf
from tensorflow import keras
import json
import os
import tempfile
import numpy as np
import base64

from rafiki.dataset import load_dataset
from rafiki.model import BaseModel, InvalidModelParamsException, test_model

class SingleHiddenLayerTensorflowModel(BaseModel):

    def get_knob_config(self):
        return {
            'knobs': {
                'hidden_layer_units': {
                    'type': 'int',
                    'range': [2, 128]
                },
                'epochs': {
                    'type': 'int',
                    'range': [1, 1]
                },
                'learning_rate': {
                    'type': 'float_exp',
                    'range': [1e-5, 1e-1]
                },
                'batch_size': {
                    'type': 'int_cat',
                    'values': [1, 2, 4, 8, 16, 32, 64, 128]
                }
            }
        }

    def init(self, knobs):
        self._batch_size = knobs.get('batch_size')
        self._epochs = knobs.get('epochs')
        self._hidden_layer_units = knobs.get('hidden_layer_units')
        self._learning_rate = knobs.get('learning_rate')

        self._graph = tf.Graph()
        self._sess = tf.Session(graph=self._graph)
        
        
    def train(self, dataset_uri):
        (images, labels) = self._load_dataset(dataset_uri)

        num_classes = len(np.unique(labels))

        X = images
        y = keras.utils.to_categorical(
            labels, 
            num_classes=num_classes
        )

        with self._graph.as_default():
            self._model = self._build_model(num_classes)
            with self._sess.as_default():
                self._model.fit(
                    X, 
                    y, 
                    epochs=self._epochs, 
                    batch_size=self._batch_size
                )

    def evaluate(self, dataset_uri):
        (images, labels) = self._load_dataset(dataset_uri)

        num_classes = len(np.unique(labels))

        X = images
        y = keras.utils.to_categorical(
            labels, 
            num_classes=num_classes
        )

        preds = self.predict(X)

        accuracy = sum(labels == preds) / len(y)
        return accuracy


    def predict(self, queries):
        X = np.array(queries)
        with self._graph.as_default():
            with self._sess.as_default():
                probs = self._model.predict(X)
                preds = np.argmax(probs, axis=1)

        return preds

    def destroy(self):
        self._sess.close()

    def dump_parameters(self):
        # TODO: Not save to & read from a file 

        # Save whole model to temp h5 file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        with self._graph.as_default():
            with self._sess.as_default():
                self._model.save(tmp.name)
        
        # Read from temp h5 file & encode it to base64 string
        with open(tmp.name, 'rb') as f:
            h5_model_bytes = f.read()

        h5_model_base64 = base64.b64encode(h5_model_bytes).decode('utf-8')

        # Remove temp file
        os.remove(tmp.name)

        return {
            'h5_model_base64': h5_model_base64
        }

    def load_parameters(self, params):
        h5_model_base64 = params.get('h5_model_base64', None)

        if h5_model_base64 is None:
            raise InvalidModelParamsException()

        # TODO: Not save to & read from a file 

        # Convert back to bytes & write to temp file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        h5_model_bytes = base64.b64decode(h5_model_base64.encode('utf-8'))
        with open(tmp.name, 'wb') as f:
            f.write(h5_model_bytes)

        # Load model from temp file
        with self._graph.as_default():
            with self._sess.as_default():
                self._model = keras.models.load_model(tmp.name)
        
        # Remove temp file
        os.remove(tmp.name)


    def _load_dataset(self, dataset_uri):
        # Here, we use Rafiki's in-built dataset loader
        return load_dataset(dataset_uri) 

    def _build_model(self, num_classes):
        hidden_layer_units = self._hidden_layer_units
        learning_rate = self._learning_rate

        model = keras.Sequential()
        model.add(keras.layers.Flatten())
        model.add(keras.layers.BatchNormalization())
        model.add(keras.layers.Dense(
            hidden_layer_units,
            activation=tf.nn.relu
        ))
        model.add(keras.layers.Dense(
            num_classes, 
            activation=tf.nn.softmax
        ))
        
        model.compile(
            optimizer=keras.optimizers.Adam(lr=learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model


if __name__ == '__main__':
    test_model(
        model_class=SingleHiddenLayerTensorflowModel,
        train_dataset_uri='tf-keras://fashion_mnist?train_or_test=train',
        test_dataset_uri='tf-keras://fashion_mnist?train_or_test=test',
        queries=[
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 0, 7, 0, 37, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 27, 84, 11, 0, 0, 0, 0, 0, 0, 119, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 88, 143, 110, 0, 0, 0, 0, 22, 93, 106, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 53, 129, 120, 147, 175, 157, 166, 135, 154, 168, 140, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 11, 137, 130, 128, 160, 176, 159, 167, 178, 149, 151, 144, 0, 0], 
            [0, 0, 0, 0, 0, 0, 1, 0, 2, 1, 0, 3, 0, 0, 115, 114, 106, 137, 168, 153, 156, 165, 167, 143, 157, 158, 11, 0], 
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3, 0, 0, 89, 139, 90, 94, 153, 149, 131, 151, 169, 172, 143, 159, 169, 48, 0], 
            [0, 0, 0, 0, 0, 0, 2, 4, 1, 0, 0, 0, 98, 136, 110, 109, 110, 162, 135, 144, 149, 159, 167, 144, 158, 169, 119, 0], 
            [0, 0, 2, 2, 1, 2, 0, 0, 0, 0, 26, 108, 117, 99, 111, 117, 136, 156, 134, 154, 154, 156, 160, 141, 147, 156, 178, 0], 
            [3, 0, 0, 0, 0, 0, 0, 21, 53, 92, 117, 111, 103, 115, 129, 134, 143, 154, 165, 170, 154, 151, 154, 143, 138, 150, 165, 43], 
            [0, 0, 23, 54, 65, 76, 85, 118, 128, 123, 111, 113, 118, 127, 125, 139, 133, 136, 160, 140, 155, 161, 144, 155, 172, 161, 189, 62], 
            [0, 68, 94, 90, 111, 114, 111, 114, 115, 127, 135, 136, 143, 126, 127, 151, 154, 143, 148, 125, 162, 162, 144, 138, 153, 162, 196, 58], 
            [70, 169, 129, 104, 98, 100, 94, 97, 98, 102, 108, 106, 119, 120, 129, 149, 156, 167, 190, 190, 196, 198, 198, 187, 197, 189, 184, 36], 
            [16, 126, 171, 188, 188, 184, 171, 153, 135, 120, 126, 127, 146, 185, 195, 209, 208, 255, 209, 177, 245, 252, 251, 251, 247, 220, 206, 49], 
            [0, 0, 0, 12, 67, 106, 164, 185, 199, 210, 211, 210, 208, 190, 150, 82, 8, 0, 0, 0, 178, 208, 188, 175, 162, 158, 151, 11], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        ]
    )
