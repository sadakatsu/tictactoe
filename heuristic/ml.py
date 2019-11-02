import numpy as np
import tensorflow as tf

layers = tf.keras.layers
models = tf.keras.models

Add = layers.Add
BatchNormalization = layers.BatchNormalization
Convolution2D = layers.Convolution2D
Dense = layers.Dense
ELU = layers.ELU
Flatten = layers.Flatten
Input = layers.Input
Reshape = layers.Reshape
Softmax = layers.Softmax
ZeroPadding2D = layers.ZeroPadding2D

load_model = models.load_model
Model = models.Model

SGD = tf.keras.optimizers.SGD
l2 = tf.keras.regularizers.l2

class DeepModel:
    def __init__(
        self,
        state_to_input,
        output_to_score,
        score_to_output,
        source: str = None,
        input: tuple = None,
        actions: int = None,
        outcomes: int = None,
        features: int = 256,
        blocks: int = 39,
        elu_alpha: float = 1.0,
        l2_lambda: float = 1e-4,
        sgd_eta: float = 0.01
    ):
        self._state_to_input = state_to_input
        self._output_to_score = output_to_score
        self._score_to_output = score_to_output

        if source:
            self._model = load_model(source)
        else:
            def activate(X):
                return ELU(elu_alpha)(X)

            def add(a, b):
                return Add()([a, b])

            def convolve(X):
                return Convolution2D(
                    filters=features,
                    kernel_size=(3, 3),
                    kernel_regularizer=l2(l2_lambda),
                    bias_regularizer=l2(l2_lambda)
                )(X)

            def dense(X, outputs, activation, name=None):
                return Dense(
                    outputs,
                    activation=activation,
                    kernel_regularizer=l2(l2_lambda),
                    bias_regularizer=l2(l2_lambda),
                    name=name
                )(X)

            def flatten(X):
                return Flatten()(X)

            def normalize(X):
                return BatchNormalization()(X)

            def pad(X):
                return ZeroPadding2D()(X)

            def convolution_block(X):
                convolved = convolve(X)
                normalized = normalize(convolved)
                activated = activate(normalized)
                padded = pad(activated)
                return activated, padded

            def residual_block(X, X_padded, add_padding=True):
                first_convolution = convolve(X_padded)
                first_normalized = normalize(first_convolution)
                first_activated = activate(first_normalized)
                first_padded = pad(first_activated)
                second_convolution = convolve(first_padded)
                second_normalized = normalize(second_convolution)
                added = add(X, second_normalized)
                activated = activate(added)
                padded = pad(activated) if add_padding else None
                return activated, padded

            def prediction_head(X):
                logits = dense(X, actions * outcomes, 'linear')
                reshaped = Reshape((actions, outcomes))(logits)
                return Softmax(axis=2, name='predictions')(reshaped)

            def loss_head(X):
                return dense(X, actions, 'relu', name='losses')

            start = Input(batch_shape=(None,) + input)

            activated, padded = convolution_block(start)
            for i in range(blocks):
                activated, padded = residual_block(activated, padded, add_padding=i + 1 < blocks)
            layer = flatten(activated)

            prediction_output = prediction_head(layer)
            loss_output = loss_head(layer)

            self._model = Model(inputs=start, outputs=[prediction_output, loss_output])
            self._model.compile(
                SGD(learning_rate=sgd_eta),
                loss={'predictions': 'categorical_crossentropy', 'losses': 'mse'}
            )

        print(self._model.summary())

    def score(self, states):
        if not isinstance(states, list):
            states = [states]
        inputs = np.array([self._state_to_input(state) for state in states])
        outputs = self._model.predict(inputs)
        return [self._output_to_score(output[0], output[1]) for output in outputs]


heuristic = DeepModel(None, None, None, input=(5, 5, 5), actions=9, outcomes=4, features=32, blocks=3)
