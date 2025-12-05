from flask import Flask, request, jsonify
from joblib import load
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    model = load('text_classifier.joblib')
    logger.info('Model loaded')
except Exception as e:
    logger.exception('Failed loading model')
    model = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok' if model is not None else 'no-model'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        logger.info('Request json: %s', data)
        text = (data or {}).get('text', '')
        if model is None:
            return jsonify({'error': 'model not loaded'}), 500
        prediction = model.predict([text])[0]
        return jsonify({'prediction': int(prediction)})
    except Exception:
        logger.exception('Prediction error')
        return jsonify({'error': 'internal'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)