import json
import requests

# Load input data
with open('cost_input.json') as f:
    payload = json.load(f)

# URL of the Flask endpoint
url = "http://127.0.0.1:5000/api/audit/cost"

# Send the POST request
response = requests.post(url, json=payload)

# Print the result
print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2))
