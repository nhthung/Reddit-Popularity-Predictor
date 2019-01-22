# -*- coding: utf-8 -*-
import json
import pickle
import numpy as np
from pathlib import Path

project_dir = Path(__file__).resolve().parents[2]
feature_names = [
    'X_counts',
    'y', # popularity_score
    ]

def main():
    paths = (project_dir / 'data' / 'processed').glob('*.json')
    for path in paths:
        file_prefix = get_file_prefix(path)
        dataset = get_dataset(path)
        features = get_features(dataset)
        write_to_file(features, file_prefix)


def get_file_prefix(path):
    return str(path).split('/')[-1].split('_')[0]


def get_dataset(path):
    with open(path) as f:
        dataset = json.load(f)
    return dataset


def get_features(dataset):
    X_counts = []
    y = []

    for data in dataset:
        X_counts.append(data['x_counts'])
        y.append([data['popularity_score']])

    X_counts = np.array(X_counts)
    y = np.array(y)

    return X_counts, y


def write_to_file(features, file_prefix):
    output_path = project_dir / 'src' / 'features'
    for feature, name in zip(features, feature_names):
        with open(output_path / (file_prefix+'_'+name+'.json'), 'wb') as fout:
            pickle.dump(feature, fout)


if __name__ == '__main__':
    main()
