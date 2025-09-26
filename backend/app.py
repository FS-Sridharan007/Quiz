from flask import Flask, jsonify
from flask_cors import CORS
import random
from question_bank import finance_questions, marketing_questions

app = Flask(__name__)
CORS(app)  # This allows requests from any origin

question_banks = {
    "finance": finance_questions,
    "marketing": marketing_questions,
    # add other sectors here
}

@app.route('/api/quiz/<sector>')
def get_quiz(sector):
    if sector not in question_banks:
        return jsonify({"error": "Sector not available"}), 400
    selected = random.sample(question_banks[sector], 10)
    return jsonify(selected)

if __name__ == "__main__":
    app.run(debug=True)
