import json

with open('/mount/src/statistics_festival/service_account.json', 'r') as f:
    data = json.load(f)

print("private_key 일부:")
print(data['private_key'][:50])  # private_key 앞부분만 출력
print("repr로 확인:")
print(repr(data['private_key'][:50]))
