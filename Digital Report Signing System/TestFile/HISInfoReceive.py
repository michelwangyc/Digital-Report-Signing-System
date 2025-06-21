from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET

app = Flask(__name__)

# 解析 HIS 发送的 XML 病人信息
def parse_patient_info(xml_data):
    try:
        root = ET.fromstring(xml_data)
        patient_info = {}

        # 解析患者基本信息
        patient_node = root.find(".//PATPatientInfo")
        if patient_node is not None:
            patient_info["HospitalCode"] = patient_node.findtext("HospitalCode", default="")
            patient_info["PatientID"] = patient_node.findtext("PATPatientID", default="")
            patient_info["Name"] = patient_node.findtext("PATName", default="")
            patient_info["DOB"] = patient_node.findtext("PATDob", default="")
            patient_info["Age"] = patient_node.findtext("PATAge", default="")
            patient_info["Sex"] = patient_node.findtext("PATSexDesc", default="")
            patient_info["Address"] = patient_node.findtext("PATAddress", default="")
            patient_info["IdentityNum"] = patient_node.findtext("PATIdentityNum", default="")

        # 解析就诊信息
        visit_node = root.find(".//PATAdmInfo")
        if visit_node is not None:
            patient_info["VisitNumber"] = visit_node.findtext("PAADMVisitNumber", default="")
            patient_info["DoctorName"] = visit_node.findtext("PAADMDocDesc", default="")
            patient_info["VisitDate"] = visit_node.findtext("PAADMStartDate", default="")
            patient_info["VisitDept"] = visit_node.findtext("PAADMDeptDesc", default="")

        return patient_info
    except Exception as e:
        print(f"XML 解析错误: {e}")
        return None

# 处理 HIS 发送的数据
@app.route("/his/patient_info", methods=["POST"])
def receive_patient_info():
    if not request.data:
        return jsonify({"error": "No data received"}), 400

    xml_data = request.data.decode("utf-8")
    patient_info = parse_patient_info(xml_data)

    if patient_info is None:
        return jsonify({"error": "Invalid XML format"}), 400

    print("接收到患者信息:", patient_info)
    
    # 这里可以将数据存入数据库或者进行其他处理
    return jsonify({"status": "success", "received": patient_info}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)