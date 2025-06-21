import json
import hmac
import hashlib
import base64

appId = "APP_7B3F36A14E99410A80B37AEF332E3247"
secret = "DLwiH46Esb8ccNTkuSSVAadNTWUfW0sc"

def sort_json_by_ascii(json_obj):
    # 对 JSON 对象的键进行排序
    sorted_json_obj = {k: json_obj[k] for k in sorted(json_obj)}
    
    # 将排序后的 JSON 对象转换为字符串
    query_string = '&'.join(f"{k}={v}" for k, v in sorted_json_obj.items())
    
    # 创建 HMAC 对象
    hmac_obj = hmac.new(secret.encode(), query_string.encode(), hashlib.sha256)

     # 获取 HMAC 的二进制值
    hmac_binary = hmac_obj.digest()

    # 进行 Base64 编码
    hmac_base64 = base64.b64encode(hmac_binary).decode()
    
    return hmac_base64

    # 示例 JSON 对象
'''
example_json = {
    "appId": appId,
    "name": "Alice",
    "age": 30,
    "userId":"2313",
    "email":"123@qq.com"
}
'''

# 生成签名
##signature = sort_json_by_ascii(example_json)

# 将签名添加到 JSON 对象中
#example_json["signature"] = signature

# 打印最终的 JSON 对象
#print(json.dumps(example_json, ensure_ascii=False, indent=4))