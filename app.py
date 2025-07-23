from flask import Flask, request, jsonify, render_template
from services.cost_audit import run_cost_audit
from services.security_audit import run_security_audit

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/status')
def status():
    return {'status': 'OK'}, 200

@app.route('/api/audit/cost', methods=['POST', 'GET'])
def cost_audit():
    if request.method == 'GET':
        return jsonify({"message": "Use POST to run the cost audit."}), 200
    data = request.get_json()
    result = run_cost_audit(data['profile'], data['region'], data.get('dry_run', False))
    return jsonify(result)
@app.route('/api/audit/security', methods=['GET', 'POST'])
def security_audit():
    if request.method == 'GET':
        return jsonify({"message": "Use POST method to run security audit"}), 200

    data = request.get_json()
    result = run_security_audit(data['profile'], data['region'], data.get('dry_run', False))
    return jsonify(result)
if __name__ == '__main__':
    app.run(debug=True)
