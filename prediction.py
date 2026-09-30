import pickle
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'final_model.sav')

def detecting_fake_news(var):
    """Predicts whether the given statement is True (Real) or False (Fake) with confidence."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    
    with open(MODEL_PATH, 'rb') as f:
        load_model = pickle.load(f)
    
    prediction = load_model.predict([var])[0]
    prob = load_model.predict_proba([var])[0]
    
    # Class order is typically [False, True]
    classes = list(load_model.classes_)
    true_index = classes.index(True) if True in classes else 1
    false_index = classes.index(False) if False in classes else 0
    
    truth_score = prob[true_index]
    fake_score = prob[false_index]
    
    is_real = bool(prediction == True or prediction == 1 or str(prediction).lower() == 'true')
    
    result = {
        'prediction': 'REAL' if is_real else 'FAKE',
        'is_real': is_real,
        'truth_prob': truth_score,
        'fake_prob': fake_score,
        'confidence': max(truth_score, fake_score) * 100
    }
    
    label_text = "Real News" if is_real else "Fake News"
    print(f"\nThe given statement is: {label_text}")
    print(f"Truth probability score: {truth_score * 100:.2f}%")
    print(f"Confidence score: {result['confidence']:.2f}%")
    return result

if __name__ == '__main__':
    user_input = input("Please enter the news text you want to verify: ").strip()
    if user_input:
        print("You entered: " + user_input)
        detecting_fake_news(user_input)
    else:
        print("No text entered.")