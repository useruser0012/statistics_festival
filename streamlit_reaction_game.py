import json

with open("service_account.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print(data["private_key"])
