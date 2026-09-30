"""
scripts/train_incremental.py
============================
Online / Incremental Learning pipeline using:
  HashingVectorizer(n_features=65536, alternate_sign=False)
      ↓
  SGDClassifier(loss='log_loss')
      ↓
  partial_fit()

Memory efficient: Fixed feature space (2^16), streams data in batches.
Compatible with scikit-learn 1.9.1.
"""

import os
import time
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'ml_models', 'current')
TRAIN_CSV = os.path.join(BASE_DIR, 'train.csv')
TEST_CSV = os.path.join(BASE_DIR, 'test.csv')

N_FEATURES = 2 ** 16  # 65536 features
BATCH_SIZE = 1000
CLASSES = np.array([0, 1])


def parse_label(val):
    if isinstance(val, (bool, np.bool_)):
        return 1 if val else 0
    s = str(val).strip().lower()
    return 1 if s in ('true', '1', 'mostly-true', 'half-true', 'real') else 0


def run_training():
    os.makedirs(MODEL_DIR, exist_ok=True)
    start_time = time.time()
    print("[1/4] Initializing HashingVectorizer and SGDClassifier...")

    vectorizer = HashingVectorizer(
        n_features=N_FEATURES,
        alternate_sign=False,
        norm='l2',
        ngram_range=(1, 2)
    )

    sgd = SGDClassifier(
        loss='log_loss',  # Logistic regression loss supporting partial_fit
        max_iter=20,
        alpha=1e-4,
        random_state=42
    )

    print(f"[2/4] Streaming training data from {TRAIN_CSV} in batches of {BATCH_SIZE}...")
    df_train = pd.read_csv(TRAIN_CSV)
    df_train.dropna(subset=['Statement', 'Label'], inplace=True)

    X_train_raw = df_train['Statement'].astype(str).tolist()
    y_train = [parse_label(l) for l in df_train['Label']]

    total_samples = len(X_train_raw)
    first_batch = True

    for i in range(0, total_samples, BATCH_SIZE):
        batch_texts = X_train_raw[i:i + BATCH_SIZE]
        batch_labels = y_train[i:i + BATCH_SIZE]
        X_batch = vectorizer.transform(batch_texts)

        if first_batch:
            sgd.partial_fit(X_batch, batch_labels, classes=CLASSES)
            first_batch = False
        else:
            sgd.partial_fit(X_batch, batch_labels)

    print(f"      Trained on {total_samples} samples.")

    print(f"[3/4] Evaluating on held-out test set {TEST_CSV}...")
    df_test = pd.read_csv(TEST_CSV)
    df_test.dropna(subset=['Statement', 'Label'], inplace=True)

    X_test_raw = df_test['Statement'].astype(str).tolist()
    y_test = [parse_label(l) for l in df_test['Label']]

    X_test = vectorizer.transform(X_test_raw)
    y_pred = sgd.predict(X_test)

    acc = round(float(accuracy_score(y_test, y_pred)), 4)
    prec = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
    rec = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
    f1 = round(float(f1_score(y_test, y_pred, zero_division=0)), 4)

    print(f"      Accuracy  : {acc * 100:.2f}%")
    print(f"      Precision : {prec * 100:.2f}%")
    print(f"      Recall    : {rec * 100:.2f}%")
    print(f"      F1 Score  : {f1 * 100:.2f}%")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Fake (0)', 'Real (1)']))

    print("[4/4] Saving model to ml_models/current/...")
    model_save_path = os.path.join(MODEL_DIR, 'sgd_logistic.pkl')
    meta_save_path = os.path.join(MODEL_DIR, 'hashing_meta.pkl')

    joblib.dump(sgd, model_save_path)
    joblib.dump({'n_features': N_FEATURES, 'ngram_range': (1, 2)}, meta_save_path)

    # Also mirror to legacy dir for backward compatibility
    legacy_dir = os.path.join(BASE_DIR, 'accounts', 'ml_models')
    if os.path.exists(legacy_dir):
        joblib.dump(sgd, os.path.join(legacy_dir, 'sgd_logistic.pkl'))
        joblib.dump({'n_features': N_FEATURES, 'ngram_range': (1, 2)}, os.path.join(legacy_dir, 'hashing_meta.pkl'))

    # Update metadata.json
    metadata_path = os.path.join(MODEL_DIR, 'metadata.json')
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except Exception:
        metadata = {'model_version': '2.0.0', 'classifiers': {}}

    metadata['classifiers']['sgd_incremental'] = {
        'path': 'sgd_logistic.pkl',
        'algorithm': "SGDClassifier(loss='log_loss')",
        'vectorizer': 'HashingVectorizer(2^16 features)',
        'features': N_FEATURES,
        'supports_partial_fit': True,
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1_score': f1,
        'trained_samples': total_samples,
        'training_time_seconds': round(time.time() - start_time, 2)
    }

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"[DONE] Incremental SGD model saved successfully -> {model_save_path}")


if __name__ == '__main__':
    run_training()
