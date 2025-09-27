from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import os

app = Flask(__name__)
CORS(app)

# ---- Configure Gemini with service account JSON ----
# Make sure the environment variable GOOGLE_APPLICATION_CREDENTIALS is set
# Example in PowerShell:
# $env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\Sridh\Downloads\secure-gizmo-473405-m8-2aacbed7789c.json"
genai.configure()

# ---- AI Quiz Generation Endpoint ----
@app.route('/api/quiz/ai', methods=["POST"])
def create_quiz_ai():
    try:
        data = request.json
        company = data.get("company")
        sector = data.get("sector")

        # ---- Validation ----
        if not company or not sector:
            return jsonify({"error": "company and sector are required"}), 400

        if sector.lower() not in ["marketing", "finance"]:
            return jsonify({"error": "Only marketing or finance sectors allowed"}), 400

        # ---- Generate Quiz using Gemini ----
        model_name = "gemini-2.5-pro"  # Replace with your available model
        model = genai.GenerativeModel(model_name)

        prompt = f"""
        Generate exactly 10 multiple choice quiz questions for the {sector} sector.
        Each question must include:
        - "question": string
        - "options": list of 4 strings
        - "answer": string
        Return a JSON array of 10 objects only, no extra text.
        """

        response = model.generate_content(prompt)
        quiz_data = response.text.strip()

        # ---- Remove triple backticks if present ----
        if quiz_data.startswith("```") and quiz_data.endswith("```"):
            quiz_data = quiz_data[3:-3].strip()

        # ---- Remove any leading non-JSON prefix (like "json\n") ----
        if quiz_data.lower().startswith("json"):
            quiz_data = quiz_data[4:].strip()

        # ---- Convert Gemini output to JSON ----
        try:
            questions = json.loads(quiz_data)
        except Exception:
            return jsonify({"error": "Gemini returned invalid JSON", "raw": quiz_data}), 500

        # ---- Ensure exactly 10 questions ----
        if len(questions) != 10:
            return jsonify({"error": f"Gemini returned {len(questions)} questions, expected 10", "raw": quiz_data}), 500

        # ---- Return Quiz ----
        return jsonify({
            "company": company,
            "sector": sector,
            "mode": "AI",
            "questions": questions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
