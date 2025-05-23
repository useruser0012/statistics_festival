import json

with open('service_account.json', 'r') as f:
    data = json.load(f)

print(data['private_key'])
