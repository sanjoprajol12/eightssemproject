from flask import Flask, render_template, request
import pickle
import os

app = Flask(__name__, template_folder='./templates', static_folder='./static')

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'final_model.sav')

# Load the model once at startup
with open(MODEL_PATH, 'rb') as f:
    loaded_model = pickle.load(f)

def fake_news_det(news):
    """Use the trained TF-IDF + Logistic Regression pipeline to predict."""
    prediction = loaded_model.predict([news])[0]
    prob = loaded_model.predict_proba([news])[0]

    classes = list(loaded_model.classes_)
    true_index = classes.index(True) if True in classes else 1
    false_index = classes.index(False) if False in classes else 0

    truth_score = prob[true_index]
    fake_score  = prob[false_index]

    is_real = bool(
        prediction is True
        or prediction == 1
        or str(prediction).lower() == 'true'
    )

    return {
        'prediction':    'REAL NEWS ✅' if is_real else 'FAKE NEWS ⚠️',
        'is_real':       is_real,
        'truth_prob_pct': round(truth_score * 100, 1),
        'fake_prob_pct':  round(fake_score  * 100, 1),
        'confidence':    round(max(truth_score, fake_score) * 100, 1),
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form.get('news', '').strip()
        if not message:
            return render_template('index.html', error="Please enter a news statement.")
        result = fake_news_det(message)
        return render_template(
            'index.html',
            prediction      = result['prediction'],
            is_real         = result['is_real'],
            truth_prob_pct  = result['truth_prob_pct'],
            fake_prob_pct   = result['fake_prob_pct'],
            confidence      = result['confidence'],
            news_text       = message,
        )
    return render_template('index.html')

if __name__ == '__main__':
    print("\n[OK] TruthLens Fake News Detector")
    print("   Running at  http://127.0.0.1:5000\n")
    app.run(debug=True, use_reloader=False)