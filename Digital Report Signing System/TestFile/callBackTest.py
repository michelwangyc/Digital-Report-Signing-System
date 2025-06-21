import requests
import json
import base64
from SignatureUtil import sort_json_by_ascii
# API 地址
url = "https://newcoss-dev.isignet.cn:10201/coss/service/v1/getSignResult"

# PDF 文件路径
pdf_file_path = "/Users/michaelwang/Desktop/华西project/TestFile/TestPDF.pdf"

# 回调地址
call_back_url = "http://localhost:8080/callback"  # 将此替换为你的实际回调地址

# 将 PDF 文件转换为 Base64 字符串
with open(pdf_file_path, "rb") as pdf_file:
    base64_data = base64.b64encode(pdf_file.read()).decode('utf-8')


param = {
    "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
    "signAlgo": "HMACSHA256",
    "signSealType": "BJCA_SM2",
    "userId": "98262c15d92f12da2e79c722deb0e470ab8f22234b88476610ef2dcdaec408ce",
    "algo": "SM3withSM2",
    "description": "描述",
    "expiryDate": "1440",
    "requireQrCode": "N",
    "pdfFileStr": base64_data,
    "sealSignPdfWaterMark": {
        "content": "批准了",
        "type": 1,
        "positionX": 10,
        "positionY": 400,
        "percent": 50
    },
    "configureSealInfo": {
        "signType": "个人签章",
        "signProvince": "北京",
        "signName": "张浩"
    },
    "coordOfRuleInfo": {
        "top": 300,
        "right": 600,
        "bottom": 200,
        "left": 350,
        "pageNo": 1
    },
    "appName": "协同签名 APPID",
    "signWidth": 150,
    "signHeight": 120,
    "opacityOfEffect": 40,
    "coverTextOfEffect": False,
    "requireTss": "N",
    "version": "2.0.9",
}


signatureV = sort_json_by_ascii(param)


# 请求参数
payload = {
    "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
    "signAlgo": "HMACSHA256",
    "signature": signatureV,
    "signSealType": "BJCA_SM2",
    "userId": "98262c15d92f12da2e79c722deb0e470ab8f22234b88476610ef2dcdaec408ce",
    "algo": "SM3withSM2",
    "description": "描述",
    "expiryDate": "1440",
    "requireQrCode": "N",
    "pdfFileStr": base64_data,
    "sealSignPdfWaterMark": {
        "content": "批准了",
        "type": 1,
        "positionX": 10,
        "positionY": 400,
        "percent": 50
    },
    "configureSealInfo": {
        "signType": "个人签章",
        "signProvince": "北京",
        "signName": "张浩"
    },
    "coordOfRuleInfo": {
        "top": 300,
        "right": 600,
        "bottom": 200,
        "left": 350,
        "pageNo": 1
    },
    "appName": "协同签名 APPID",
    "signWidth": 150,
    "signHeight": 120,
    "opacityOfEffect": 40,
    "coverTextOfEffect": False,
    "requireTss": "N",
    "version": "2.0.9",
}

# 设置请求头
headers = {
    "Content-Type": "application/json"
}

try:
    # 发送 POST 请求
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    # 检查响应状态码并打印结果
    if response.status_code == 200:
        print("请求成功:", response.json()['message'], response.json()['data']['signDataId'], response.json()['data']['signResult'])

        composePdf = response.json()['data']['composePdf']

        composePdf = composePdf.replace('\n', '')
        pdf_data = base64.b64decode(composePdf)
        output_path = '/Users/michaelwang/Desktop/华西project/TestFile/SignedTestPDF.pdf'  # 文件名和路径
        with open(output_path, 'wb') as pdf_file:
            pdf_file.write(pdf_data)

        print(f"PDF 已保存到 {output_path}")

    else:
        print(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"请求过程中出现错误: {e}")