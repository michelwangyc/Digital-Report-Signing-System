import requests
import json
from SignatureUtil import sort_json_by_ascii
# API 地址
url = "https://newcoss-dev.isignet.cn:10201/coss/service/v1/addUser"

headers = {
    "Content-Type": "application/json"
}

def addUser(name, id, idtype, phoneNumber, department):
    param = {
        "version": "1.0",
        "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
        "signAlgo": "HMAC",
        "userName": name,
        "idType": idtype,
        "idNumber": id,
        "department": department,
        "mobile": phoneNumber,
    }

    signatureV = sort_json_by_ascii(param)

    payload = {
        "version": "1.0",
        "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
        "signAlgo": "HMAC",
        "userName": name,
        "idType": idtype,
        "idNumber": id,
        "department": department,
        "mobile": phoneNumber,
        "signature": signatureV
    }

    try:
        # 发送 POST 请求
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求反馈:", response.json())
            userId = response.json()['data']['userId']
            print(userId)
            return userId

        else:
            print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"请求过程中出现错误: {e}")




param = {
    "version": "1.0",
    "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
    "signAlgo": "HMAC",
    "userName": "王振宇",
    "idType": "SF",
    "idNumber": "142601200003141334",
    "department": "QT",
    "mobile": "18435739296",
    #"signature": "NA32oYb/y5OiOWnOgy+Auo3O4Ta4MHXEQeKOJW3Vg+Q="
}

signatureV = sort_json_by_ascii(param)


# 请求参数
payload = {
    "version": "1.0",
    "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
    "signAlgo": "HMAC",
    "userName": "YuchenWzy",
    "idType": "SF",
    "idNumber": "142601200103141334",
    "department": "QT",
    "mobile": "18435739299",
    "signature": signatureV
}


try:
    # 发送 POST 请求
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        print("请求反馈:", response.json())
        userId = response.json()['data']['userId']
        print(userId)

    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"请求过程中出现错误: {e}")