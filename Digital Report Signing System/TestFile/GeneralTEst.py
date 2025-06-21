from flask import Flask, request, jsonify, render_template
import requests
import time
import threading

app = Flask(__name__)

# 模拟数据库存储
db = {
    "signdataid": None,  # 签名任务 ID
    "msspid": None,  # 用户 ID
    "signatures": [],  # 签名值记录
    "timestamps": [],  # 时间戳记录
}

# CA 服务端配置
CA_BASE_URL = "https://newcoss-dev.isignet.cn:10201/coss/service/v1/"
HEADERS = {"Content-Type": "application/json"}
APP_ID = "APP_7B3F36A14E99410A80B37AEF332E3247"
SIGN_ALGO = "HMAC"
SECURE_CODE = "your_secure_code"

def hmac_signature(data, secure_code):
    """
    使用 HMAC-SHA256 生成签名
    """
    import hmac
    import hashlib
    import base64
    encoded_data = "&".join(f"{k}={v}" for k, v in sorted(data.items()))
    signature = hmac.new(
        secure_code.encode(), encoded_data.encode(), hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode()

def call_api(endpoint, payload):
    """
    封装 API 调用
    """
    payload["appId"] = APP_ID
    payload["signAlgo"] = SIGN_ALGO
    payload["signature"] = hmac_signature(payload, SECURE_CODE)
    response = requests.post(f"{CA_BASE_URL}{endpoint}", json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()

@app.route("/")
def index():
    return render_template("index.html")

# Step 1: 开启 PDF 自动签名任务
@app.route("startAutoSign", methods=["POST"])
def start_pdf_auto_sign():
    user_id = request.json.get("userId")
    expiry = request.json.get("expiry", "1440")  # 默认 1 天
    payload = {
        "userId": user_id,
        "title": "PDF Auto Sign Authorization",
        "dataType": "WEB_SEAL",
        "algo": "SM3withSM2",
        "description": "Authorization for PDF Auto Signing",
        "expiryDate": expiry,
        "requireQrCode": "Y",
    }
    response = call_api("/coss/service/v1/addAuthSignJob", payload)
    qr_code = response["data"]["qrCode"]
    signdataid = response["data"]["signDataId"]
    db["signdataid"] = signdataid  # 保存签名任务 ID
    return jsonify({"qrCode": qr_code, "signdataid": signdataid})

# Step 2: 轮询签名任务明细
def poll_sign_detail(signdataid):
    start_time = time.time()
    while time.time() - start_time < 180:  # 最大轮询时间 3 分钟
        payload = {"signDataId": signdataid}
        response = call_api("/coss/service/v1/getSignResult", payload)
        if response["data"]["jobStatus"] == "FINISH":
            db["msspid"] = response["data"]["msspId"]  # 保存用户 ID
            return True
        time.sleep(2)  # 间隔 2 秒
    return False

@app.route("/poll_sign_status", methods=["GET"])
def poll_sign_status():
    signdataid = db.get("signdataid")
    if not signdataid:
        return jsonify({"error": "No signdataid found"}), 400
    threading.Thread(target=poll_sign_detail, args=(signdataid,)).start()
    return jsonify({"status": "Polling started"})

# Step 3: 使用 PDF 文件自动签名接口
@app.route("/pdf_sign", methods=["POST"])
def pdf_sign():
    signdataid = db.get("signdataid")
    msspid = db.get("msspid")
    if not signdataid or not msspid:
        return jsonify({"error": "Signdataid or msspid not found"}), 400

    # 从请求中获取 PDF 文件 Base64 编码
    pdf_base64 = request.json.get("pdfBase64")
    title = request.json.get("title", "PDF Signing")
    description = request.json.get("description", "Signing PDF Automatically")

    payload = {
        "signDataId": signdataid,
        "userId": msspid,
        "data": pdf_base64,
        "title": title,
        "description": description,
    }
    response = call_api("/coss/service/v1/pdfAutoSign", payload)
    signature = response["data"]["signature"]
    db["signatures"].append({"signature": signature, "cert": response["data"]["cert"]})
    return jsonify({"status": "PDF Signed", "signature": signature})

# Step 4: 保存时间戳
@app.route("/save_timestamp", methods=["POST"])
def save_timestamp():
    payload = {"data": request.json.get("data")}
    response = call_api("/coss/service/v1/addTimestamp", payload)
    db["timestamps"].append(response["data"])
    return jsonify({"status": "Timestamp saved", "timestamp": response["data"]})

# Step 5: 验证签名和时间戳
@app.route("/validate", methods=["POST"])
def validate():
    signature = request.json.get("signature")
    timestamp = request.json.get("timestamp")
    data = request.json.get("data")

    sig_response = call_api("/coss/service/v1/validateSignature", {"signature": signature, "data": data})
    ts_response = call_api("/coss/service/v1/validateTimestamp", {"timestamp": timestamp, "data": data})

    return jsonify({
        "signature_valid": sig_response["status"] == 200,
        "timestamp_valid": ts_response["status"] == 200,
    })

if __name__ == "__main__":
    app.run(debug=True)