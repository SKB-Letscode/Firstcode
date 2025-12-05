import requests

url = "http://localhost:5000/predict"
payload = {"text": "Yankees won NASA"}
#payload = {"text": "NASA launched a new satellite today and The Yankees won the baseball game yesterday"}
#payload = {"text": "The Yankees won the baseball game yesterday"}
#payload = {"text": "Sara"}
response = requests.post(url, json=payload)
print("Response:", response.json())