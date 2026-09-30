"""
train_model.py
==============
Retrain the Fake News Detection model from scratch using train.csv.
Saves the trained pipeline to final_model.sav (used by prediction.py & front.py).

Usage:
    python train_model.py
"""

import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score

# ─────────────────────────────────────────────
# 1. Paths
# ─────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
TRAIN_CSV  = os.path.join(BASE_DIR, 'train.csv')
TEST_CSV   = os.path.join(BASE_DIR, 'test.csv')
MODEL_OUT  = os.path.join(BASE_DIR, 'final_model.sav')

# ─────────────────────────────────────────────
# 2. Load Data
# ─────────────────────────────────────────────
print("[1/5] Loading data...")
train_df = pd.read_csv(TRAIN_CSV)
test_df  = pd.read_csv(TEST_CSV)

# Drop any rows with missing Statement or Label
train_df.dropna(subset=['Statement', 'Label'], inplace=True)
test_df.dropna(subset=['Statement', 'Label'], inplace=True)

print(f"      Train samples : {len(train_df)}")
print(f"      Test  samples : {len(test_df)}")
print(f"      Label classes : {train_df['Label'].unique().tolist()}")

X_train = train_df['Statement'].astype(str)
y_train = train_df['Label']

X_test  = test_df['Statement'].astype(str)
y_test  = test_df['Label']

# ─────────────────────────────────────────────
# 3. Build Pipeline
#    TF-IDF (n-grams 1..4) → Logistic Regression
# ─────────────────────────────────────────────
print("[2/5] Building pipeline...")
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 4),   # unigrams up to 4-grams
        use_idf=True,
        smooth_idf=True,
        max_features=200_000, # cap vocabulary size
    )),
    ('clf', LogisticRegression(
        C=1.0,
        solver='lbfgs',
        max_iter=1000,
    )),
])

# ─────────────────────────────────────────────
# 4. Train
# ─────────────────────────────────────────────
print("[3/5] Training model (this may take ~30-60 seconds)...")
pipeline.fit(X_train, y_train)
print("      Training complete!")

# ─────────────────────────────────────────────
# 5. Evaluate on Test Set
# ─────────────────────────────────────────────
print("[4/5] Evaluating on test set...")
y_pred   = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1       = f1_score(y_test, y_pred, average='weighted')

print(f"\n      Accuracy : {accuracy * 100:.2f}%")
print(f"      F1 Score : {f1 * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ─────────────────────────────────────────────
# 6. Save Model
# ─────────────────────────────────────────────
print("[5/5] Saving model to final_model.sav...")
with open(MODEL_OUT, 'wb') as f:
    pickle.dump(pipeline, f)

print(f"\n[DONE] Model saved -> {MODEL_OUT}")
print("       You can now run the app:  python front.py\n")
