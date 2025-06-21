import requests
import json
from SignatureUtil import sort_json_by_ascii

# API 地址
url = "https://newcoss-dev.isignet.cn:10201/coss/service/v1/queryUserInfo"

json_original = {

    "version":"1.0",
    "appId":"APP_7B3F36A14E99410A80B37AEF332E3247",
    "signAlgo":"HMAC",
    "idType":"SF",
    "idNumber":"142701200003243310",
    
}

signatureV = sort_json_by_ascii(json_original)

print('Sign Value: ')
print(signatureV)

# 请求参数
payload = {
    
    "version":"1.0",
    "appId":"APP_7B3F36A14E99410A80B37AEF332E3247",
    "signAlgo":"HMAC",
    "idType":"SF",
    "idNumber":"142701200003243310",
    "signature": signatureV
}

# 设置请求头
headers = {
    "Content-Type": "application/json"
}

try:
    # 发送 POST 请求
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功:", response.json())
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"请求过程中出现错误: {e}")