# -*- coding: utf-8 -*-
""" Authors: Le Nhat Hung, Negin Ashr """
import logging
import pickle
import numpy as np
import plotly.graph_objs as go
import plotly.plotly as py
import sys
from pathlib import Path
from models import *
import datetime

project_dir = Path(__file__).resolve().parents[2]

def main():
    """
    Create, train, and save 4 closed form models and
    4 gradient descent models for the following versions:
        1. 'no_text': no text features
        2. '60': top 60 words
        3. '160': top 160 words (basic, with stop words like 'the' or 'a' included)
        4. Top 160 words + newly added features included
    """
    logger = logging.getLogger(__name__)
    logger.info('training models')

    features_path = project_dir / 'src' / 'features'
    output_path = project_dir / 'models'
    predictions_path = project_dir / 'reports'

    X_train, \
    X_train_160, \
    X_train_60, \
    X_train_no_text, \
    Y_train = get_XY_train(features_path)

    closedForm, closedForm160, closedForm60, closedFormNoText = [ClosedForm()] * 4
    gradientDescent, gradientDescent160, gradientDescent60, gradientDescentNoText = [GradientDescent()] * 4


    """
    Train closed form top 160, top 60, no text and full models.
    The full model is:
        top 160 words + newly added features included

    We'll pick 42 as the degree of freedom for the stem feature
    (see notebook `3.0-lnh-task-3-experimentation`)
    """
    optimal_size = 42

    # Reducing stem vector's size of X_train
    X_train = reduce_stem(X_train, optimal_size)

    # Train models
    model_X_pairs = (
        (closedForm, X_train),
        (closedForm160, X_train_160),
        (closedForm60, X_train_60),
        (closedFormNoText, X_train_no_text),
    )
    closedForm, \
    closedForm160, \
    closedForm60, \
    closedFormNoText = train_models(model_X_pairs, Y_train)

    # Sve models
    model_filename_pairs = (
        (closedForm, 'ClosedForm.pkl'),
        (closedForm160, 'ClosedForm_160.pkl'),
        (closedForm60, 'ClosedForm_60.pkl'),
        (closedFormNoText, 'ClosedForm_no_text.pkl'),
    )
    save_models(model_filename_pairs, output_path)
    logger.info('finished closed form no text, top 160, top 60 models training')


    """
    Train gradient descent models
    """
    model_X_pairs = (
        (gradientDescent, X_train),
        (gradientDescent160, X_train_160),
        (gradientDescent60, X_train_60),
        (gradientDescentNoText, X_train_no_text),
    )

    # Hyperparameters
    hparams = {
        'beta': 1e-4, # prof: < 1e-3
        'eta_0': 1e-5, # prof: < 1e-5
        'eps': 1e-6,
    }
    gradientDescent, \
    gradientDescent160, \
    gradientDescent60, \
    gradientDescentNoText = train_models(model_X_pairs, Y_train, hparams=hparams)
    model_filename_pairs = (
        (gradientDescent, 'GradientDescent.pkl'),
        (gradientDescent160, 'GradientDescent_160.pkl'),
        (gradientDescent60, 'GradientDescent_60.pkl'),
        (gradientDescentNoText, 'GradientDescent_no_text.pkl'),
    )
    save_models(model_filename_pairs, output_path)
    logger.info('finished gradient descent models training')


def train_models(model_X_pairs, Y, hparams=None):
    """
    Train (model, X) pairs with target Y.
    Return trained models
    """
    models = []
    for model, X in model_X_pairs:
        if hparams is None:
            time_start = datetime.datetime.now()
            model.train(X, Y)
            time_end = datetime.datetime.now()
            model = ClosedForm(w=model.w)
        else:
            hparams['w_0'] = np.zeros((X.shape[1], 1))
            time_start = datetime.datetime.now()
            model.train(X, Y, **hparams)
            time_end = datetime.datetime.now()
            model = GradientDescent(
                w=model.w,
                hparams=model.get_hyperparams(),
                num_iterations=model.num_iterations)

        print('time: ', end='')
        print((time_end - time_start).microseconds, end=' ')
        print('ms')
        models.append(model)

    return models


def get_XY_train(features_path):
    files = [
        'training_X.pkl',
        'training_X_160.pkl',
        'training_X_60.pkl',
        'training_X_no_text.pkl',
        'training_y.pkl',
    ]
    XY_train = []

    for file in files:
        XY_train.append(pickle.load(open(features_path / file, 'rb')))

    return XY_train


def reduce_stem(X, stem_size):
    """
    Structure of a row of X_train:
    index 0: is_root
          1: controversiality
          2: children
          3: length
          4-163: x_counts
          164-323: stem
          324: bias term
    """
    stem_start = 164

    X_temp = np.array([ # 1 X matrix
        np.concatenate(( # One row
            X[i][:stem_start], # Begining of row
            X[i][stem_start:stem_start + stem_size], # Stem
            np.array([1]) # Bias term of row
        )) for i in range(X.shape[0]) # 10000 rows to create 1 X matrix
    ])
    return X_temp


def save_models(model_filename_pairs, output_path):
    for model, name in model_filename_pairs:
        if model.is_trained():
            pickle.dump(model, open(output_path / name, 'wb'))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
