import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from github_manager import save_to_github

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend (adjust origin in production)

# Configuration – you can also use environment variables
REPO_NAME = os.environ.get("REPO_NAME", "sunilpanwar/calculator_app")
FILE_PATH = os.environ.get("FILE_PATH", "calculator_results/latest.json")
BRANCH = os.environ.get("BRANCH", "develop")

@app.route('/save-results', methods=['POST'])
def save_results():
    """
    Expects JSON: {
        "principal": 100000,
        "monthly_roi": 2.5,
        "days": 100,
        "daily_less_principle": 1000,
        "daily_interest": 84,
        "daily_emi": 1084,
        "monthly_emi": 32520,
        "closure_amount": 108400,
        "timestamp": "2025-04-14T12:00:00Z"   (optional)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Basic validation
    required_fields = ['principal', 'monthly_roi', 'days', 'closure_amount']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Add a timestamp if not present
    if 'timestamp' not in data:
        from datetime import datetime
        data['timestamp'] = datetime.utcnow().isoformat() + 'Z'

    # Prepare commit message (optional: include timestamp)
    commit_msg = f"Save calculator results: {data['timestamp']}"

    # Call GitHub save function
    result = save_to_github(
        data=data,
        repo_name=REPO_NAME,
        file_path=FILE_PATH,
        commit_message=commit_msg,
        branch=BRANCH
    )

    if result['success']:
        return jsonify({
            "message": f"File {result['action']} successfully",
            "url": result['url']
        }), 200
    else:
        return jsonify({"error": result['error']}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)