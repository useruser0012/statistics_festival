import json

with open('/mount/src/statistics_festival/service_account.json', 'r') as f:
    data = json.load(f)

print(data['private_key'])
print(repr(data['private_key']))  # 문자열 내부에 \n이 어떻게 들어있는지 출력
