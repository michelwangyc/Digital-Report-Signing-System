from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET
import pyodbc
import os
import json
from queue import Queue
import threading
import time
from flask import send_file
import requests
from SignatureUtil import sort_json_by_ascii
import base64
import xml.sax.saxutils as saxutils

app = Flask(__name__)

# 设置 SQLite 数据库路径
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 创建病人信息模型
# 1. 修改 Patient 模型，删除重复的字段定义
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息 (保持不变)
    patient_id = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex_code = db.Column(db.String(10))
    sex = db.Column(db.String(10))
    marital_status_code = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    document_no = db.Column(db.String(50))
    nation_code = db.Column(db.String(10))
    nation = db.Column(db.String(50))
    address = db.Column(db.String(200))
    country_code = db.Column(db.String(10))
    country = db.Column(db.String(50))
    health_card_id = db.Column(db.String(50))
    occupation_code = db.Column(db.String(10))
    occupation = db.Column(db.String(50))
    workplace = db.Column(db.String(100))
    workplace_tel = db.Column(db.String(20))
    identity_num = db.Column(db.String(50))
    id_type_code = db.Column(db.String(10))
    id_type = db.Column(db.String(50))
    relation_name = db.Column(db.String(50))
    relation_phone = db.Column(db.String(20))
    telephone = db.Column(db.String(20))
    remarks = db.Column(db.String(500))
    
    # 就诊信息
    visit_number = db.Column(db.String(20), nullable=False)
    visit_times = db.Column(db.String(20))
    visit_type_code = db.Column(db.String(10))
    visit_type = db.Column(db.String(20))
    adm_status_code = db.Column(db.String(10))
    adm_status = db.Column(db.String(20))
    doctor_code = db.Column(db.String(20))
    doctor_name = db.Column(db.String(50))
    visit_start_date = db.Column(db.String(20))
    visit_start_time = db.Column(db.String(20))
    dept_code = db.Column(db.String(20))
    visit_dept = db.Column(db.String(50))
    ward_code = db.Column(db.String(20))
    ward_name = db.Column(db.String(50))
    bed_no = db.Column(db.String(20))
    fee_type_code = db.Column(db.String(10))
    fee_type = db.Column(db.String(20))
    hospital_code = db.Column(db.String(20))
    
    # 检查信息
    height = db.Column(db.String(10))
    weight = db.Column(db.String(10))
    clinical_symptoms = db.Column(db.String(500))

    # 添加新字段
    source_system = db.Column(db.String(10))
    message_id = db.Column(db.String(20))
    # 添加新的系统信息字段
    source_system = db.Column(db.String(10))
    message_id = db.Column(db.String(20))
    
    # 添加新的医嘱信息字段
    order_item_id = db.Column(db.String(50))
    order_status_code = db.Column(db.String(10))
    order_sub_cat_code = db.Column(db.String(10))
    order_sub_cat_desc = db.Column(db.String(50))
    order_cat_code = db.Column(db.String(10))
    order_cat_desc = db.Column(db.String(50))
    parent_order_id = db.Column(db.String(50))
    service_method = db.Column(db.String(10))
    arcim = db.Column(db.String(50))
    update_user_code = db.Column(db.String(20))
    update_user_desc = db.Column(db.String(50))
    update_date = db.Column(db.String(20))
    update_time = db.Column(db.String(20))
    
    status = db.Column(db.String(20), nullable=False, default="pending")
    completed_time = db.Column(db.DateTime)  # 添加完成时间字段
    signed_pdf = db.Column(db.Text)  # 添加用于存储签名后的PDF数据的字段

    # 添加医疗信息字段
    chaint = db.Column(db.String(500))
    mehistory = db.Column(db.String(500))
    hemogram = db.Column(db.String(500))
    mesituation = db.Column(db.String(500))
    inspresults = db.Column(db.String(500))
    chestpain = db.Column(db.String(500))
    phycycle = db.Column(db.String(500))
    pat_type = db.Column(db.String(50))
    pat_tag = db.Column(db.String(50))
    admission_type = db.Column(db.String(50))

    def __repr__(self):
        return f"<Patient {self.name}>"

# 创建数据库
with app.app_context():
    db.create_all()

# 接收病人信息并存入数据库
# 创建一个队列
message_queue = Queue()

# 处理队列中消息的函数
def process_queue():
    with app.app_context():
        while True:
            if not message_queue.empty():
                xml_data, root = message_queue.get()
                try:
                    # 识别消息类型
                    message_types = {
                        "AddRisAppBillRt": handle_add_ris_app_bill,
                        "UpdateOrdersRt": handle_update_orders_status,
                        "RisRegistry": handle_ris_registry,
                        "RegisterDocument": handle_register_document,
                        "OrderStatusRt": handle_order_status_rt
                    }
                    
                    # 检查消息类型并处理
                    for msg_type, handler in message_types.items():
                        if root.find(f".//{msg_type}") is not None:
                            result = handler(root)
                            print(f"处理结果: {result}")  # 添加日志
                            break
                    
                except Exception as e:
                    print(f"处理消息时出错: {str(e)}")  # 添加错误日志
                finally:
                    message_queue.task_done()
            time.sleep(0.1)  # 避免过度消耗 CPU

# 修改接收接口
@app.route("/his/patient_info", methods=["POST"])
def receive_patient_info():
    if not request.data:
        return "No data received", 400

    try:
        xml_data = request.data.decode("utf-8")
        root = ET.fromstring(xml_data)
        # 将数据放入队列
        message_queue.put((xml_data, root))
        print(f"消息已加入队列，当前队列长度: {message_queue.qsize()}")  # 添加日志
        return "Message queued for processing", 202
    except Exception as e:
        print(f"接收消息时出错: {str(e)}")  # 添加错误日志
        return f"Error receiving message: {str(e)}", 500

def handle_add_ris_app_bill(root):
    try:
        # 获取系统信息
        header = root.find(".//Header")
        source_system = header.find("SourceSystem").text
        message_id = header.find("MessageID").text

        # 构建病人信息字典
        patient_info = {
            # 系统信息
            'source_system': source_system,
            'message_id': message_id,
            
            # 基本信息
            'patient_id': root.find(".//PATPatientID").text,
            'name': root.find(".//PATName").text,
            'dob': root.find(".//PATDob").text,
            'age': root.find(".//PATAge").text,
            'sex_code': root.find(".//PATSexCode").text,
            'sex': root.find(".//PATSexDesc").text,
            'marital_status_code': root.find(".//PATMaritalStatusCode").text,
            'marital_status': root.find(".//PATMaritalStatusDesc").text,
            'document_no': root.find(".//PATDocumentNo").text or '',
            'nation_code': root.find(".//PATNationCode").text,
            'nation': root.find(".//PATNationDesc").text,
            'address': root.find(".//PATAddress").text,
            'country_code': root.find(".//PATCountryCode").text,
            'country': root.find(".//PATCountryDesc").text,
            'health_card_id': root.find(".//PATHealthCardID").text or '',
            'occupation_code': root.find(".//PATOccupationCode").text,
            'occupation': root.find(".//PATOccupationDesc").text,
            'workplace': root.find(".//PATWorkPlaceName").text or '',
            'workplace_tel': root.find(".//PATWorkPlaceTelNum").text or '',
            'identity_num': root.find(".//PATIdentityNum").text,
            'id_type_code': root.find(".//PATIdTypeCode").text,
            'id_type': root.find(".//PATIdTypeDesc").text,
            'relation_name': root.find(".//PATRelationName").text,
            'relation_phone': root.find(".//PATRelationPhone").text,
            'telephone': root.find(".//PATTelephone").text,
            'remarks': root.find(".//PATRemarks").text or '',
            
            # 就诊信息
            'visit_number': root.find(".//PAADMVisitNumber").text,
            'visit_times': root.find(".//PAADMVisitTimes").text or '',
            'visit_type_code': root.find(".//PAADMTypeCode").text,
            'visit_type': root.find(".//PAADMTypeDesc").text,
            'adm_status_code': root.find(".//PAAdmStatusCode").text,
            'adm_status': root.find(".//PAAdmStatusDesc").text,
            'doctor_code': root.find(".//PAADMDocCode").text,
            'doctor_name': root.find(".//PAADMDocDesc").text,
            'visit_start_date': root.find(".//PAADMStartDate").text,
            'visit_start_time': root.find(".//PAADMStartTime").text,
            'dept_code': root.find(".//PAADMDeptCode").text,
            'visit_dept': root.find(".//PAADMDeptDesc").text,
            'ward_code': root.find(".//PAADMAdmWardCode").text,
            'ward_name': root.find(".//PAADMAdmWardDesc").text,
            'bed_no': root.find(".//PAADMCurBedNo").text or '',
            'fee_type_code': root.find(".//PAADMFeeTypeCode").text,
            'fee_type': root.find(".//PAADMFeeTypeDesc").text,
            'hospital_code': root.find(".//PAADMHosCode").text,
            
            # 医疗信息
            'chaint': root.find(".//Chaint").text if root.find(".//Chaint") is not None else '',
            'mehistory': root.find(".//Mehistory").text if root.find(".//Mehistory") is not None else '',
            'hemogram': root.find(".//Hemogram").text if root.find(".//Hemogram") is not None else '',
            'mesituation': root.find(".//Mesituation").text if root.find(".//Mesituation") is not None else '',
            'inspresults': root.find(".//Inspresults").text if root.find(".//Inspresults") is not None else '',
            'chestpain': root.find(".//Chestpain").text if root.find(".//Chestpain") is not None else '',
            'phycycle': root.find(".//Phycycle").text if root.find(".//Phycycle") is not None else '',
            'height': root.find(".//Height").text or '',
            'weight': root.find(".//weight").text or '',
            'pat_type': root.find(".//PatType").text or '',
            'pat_tag': root.find(".//Pattag").text or '',
            
            # 检查申请信息
            'clinical_symptoms': root.find(".//RISRClinicalSymptoms").text or '',
            'order_item_id': root.find(".//OEORIOrderItemID").text,
            'order_sub_cat_code': root.find(".//OrdSubCatCode").text,
            'order_sub_cat_desc': root.find(".//OrdSubCatDesc").text,
            'order_cat_code': root.find(".//OrdCatCode").text,
            'order_cat_desc': root.find(".//OrdCatDesc").text,
        }
    
        # 将病人信息存入数据库
        new_patient = Patient(**patient_info, status="pending")
        db.session.add(new_patient)
        db.session.commit()
        
        # 直接调用发送功能
        try:
            # 连接 Access 数据库
            conn = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\admin\Desktop\生物反馈\Data\MultiTrace.mdb;')
            cursor = conn.cursor()

            # 插入数据
            insert_sql = "INSERT INTO Clients (ClientID, ClientFirstName, ClientLastName) VALUES (?, ?, ?)"
            cursor.execute(insert_sql, (new_patient.patient_id, new_patient.name, ''))
            
            # 提交事务并关闭连接
            conn.commit()
            cursor.close()
            conn.close()

            # 创建病人文件夹
            folder_name = f"{new_patient.patient_id}"
            folder_path = os.path.join(r"C:\Users\admin\Desktop\生物反馈\PatientData", folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # 更新病人状态为正在处理
            new_patient.status = "processing"
            db.session.commit()
            
            print(f"自动发送病人信息成功: {new_patient.name}")
            
        except Exception as send_error:
            print(f"自动发送失败: {str(send_error)}")
            
        return "AddRisAppBill processed", 200
        
    except Exception as e:
        if 'new_patient' in locals():
            db.session.rollback()
        return f"Error processing AddRisAppBill: {str(e)}", 500

def handle_update_orders_status(root):
    try:
        # 获取病人ID和就诊号
        patient_id = root.find(".//PATPatientID").text
        visit_number = root.find(".//PAADMVisitNumber").text
        
        # 查找对应的病人记录
        patient = Patient.query.filter_by(
            patient_id=patient_id,
            visit_number=visit_number
        ).first()
        
        if not patient:
            return f"Patient not found with ID: {patient_id}", 404
            
        # 获取更新信息
        update_info = {
            # 系统信息
            'source_system': root.find(".//SourceSystem").text,
            'message_id': root.find(".//MessageID").text,
            
            # 基本信息更新
            'hospital_code': root.find(".//HospitalCode").text,
            
            # 就诊信息更新
            'visit_type_code': root.find(".//PAADMEncounterTypeCode").text,
            'doctor_code': root.find(".//OEORIStopDoc").text,
            'doctor_name': root.find(".//OEORIStopDocDesc").text,
            'dept_code': root.find(".//OEORIExecDeptCode").text,
            'visit_dept': root.find(".//OEORIExecDeptDesc").text,
            'fee_type_code': root.find(".//OEORIFeeType").text,
            
            # 更新信息
            'update_user_code': root.find(".//UpdateUserCode").text,
            'update_user_desc': root.find(".//UpdateUserDesc").text,
            'update_date': root.find(".//UpdateDate").text,
            'update_time': root.find(".//UpdateTime").text,
        }
        
        # 获取医嘱信息
        oeori_info = root.find(".//OEORIInfo")
        if oeori_info is not None:
            additional_info = {
                'order_item_id': oeori_info.find("OEORIOrderItemID").text,
                'order_status_code': oeori_info.find("OEORIStatusCode").text,
                'order_sub_cat_code': oeori_info.find("OEORIOrdSubCatCode").text,
                'order_sub_cat_desc': oeori_info.find("OEORIOrdSubCatDesc").text,
                'order_cat_code': oeori_info.find("OEORIOrdCatCode").text,
                'order_cat_desc': oeori_info.find("OEORIOrdCatDesc").text,
                'parent_order_id': oeori_info.find("OEORIParentOrderID").text,
                'service_method': oeori_info.find("OEORIServMethod").text,
                'arcim': oeori_info.find("OEORIArcim").text
            }
            update_info.update(additional_info)
        
        # 更新病人信息
        for key, value in update_info.items():
            if value is not None and hasattr(patient, key):
                setattr(patient, key, value)
        
        # 提交数据库更新
        db.session.commit()
        
        return "Order status updated successfully", 200
        
    except Exception as e:
        db.session.rollback()
        return f"Error updating order status: {str(e)}", 500

def handle_ris_registry(root):
    # 待实现
    return "RisRegistry handler not implemented", 501

def handle_register_document(root):
    # 待实现
    return "RegisterDocument handler not implemented", 501

def handle_order_status_rt(root):
    # 待实现
    return "OrderStatusRt handler not implemented", 501
    
# 显示病人的详细信息
@app.route("/patient/<int:patient_id>")
def patient_detail(patient_id):
    # 从数据库获取病人的详细信息
    patient = Patient.query.get_or_404(patient_id)
    return render_template("patient_detail.html", patient=patient)


@app.route("/view_pdf/<int:patient_id>")
def view_pdf(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        folder_path = os.path.join(r"C:\Users\admin\Desktop\生物反馈\PatientData", patient.patient_id)
        
        # 查找PDF文件
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        if pdf_files:
            pdf_path = os.path.join(folder_path, pdf_files[0])  # 获取第一个PDF文件
            return send_file(pdf_path, mimetype='application/pdf')
        else:
            return "未找到PDF报告", 404
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/get_patients")
def get_patients():
    pending_patients = Patient.query.filter_by(status="pending").all()
    processing_patients = Patient.query.filter_by(status="processing").all()
    processed_patients = Patient.query.filter_by(status="processed").all()
    
    patients_data = {
        'pending': [{'id': p.id, 'name': p.name, 'patient_id': p.patient_id} for p in pending_patients],
        'processing': [{'id': p.id, 'name': p.name, 'patient_id': p.patient_id} for p in processing_patients],
        'processed': [{
            'id': p.id, 
            'name': p.name, 
            'patient_id': p.patient_id,
            'completed_time': p.completed_time.strftime('%Y-%m-%d %H:%M:%S') if p.completed_time else ''
        } for p in processed_patients]
    }
    return jsonify(patients_data)

@app.route("/")
def index():
    pending_patients = Patient.query.filter_by(status="pending").all()
    processing_patients = Patient.query.filter_by(status="processing").all()
    processed_patients = Patient.query.filter_by(status="processed").all()
    sent_patients = Patient.query.filter_by(status="sent").all()  # 添加已发送患者查询
    
    # 合并pending和processing状态的病人
    all_pending_patients = pending_patients + processing_patients
    
    return render_template("index.html", 
                         all_pending_patients=all_pending_patients,
                         processed_patients=processed_patients,
                         sent_patients=sent_patients)  # 添加sent_patients到模板

@app.route("/send_patient/<int:patient_id>")
def send_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # 连接 Access 数据库
        conn = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\admin\Desktop\生物反馈\Data\MultiTrace.mdb;')
        cursor = conn.cursor()

        # 插入数据
        insert_sql = "INSERT INTO Clients (ClientID, ClientFirstName, ClientLastName) VALUES (?, ?, ?)"
        cursor.execute(insert_sql, (patient.patient_id, patient.name, ''))
        
        # 提交事务并关闭连接
        conn.commit()
        cursor.close()
        conn.close()

        # 创建病人文件夹 (修复变量引用错误)
        folder_name = f"{patient.patient_id}"
        folder_path = os.path.join(r"C:\Users\admin\Desktop\生物反馈\PatientData", folder_name)  # 这里修改了错误
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 更新病人状态为正在处理
        patient.status = "processing"
        db.session.commit()

        return jsonify({"success": True, "message": "患者信息已成功发送"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def monitor_processed_patients():
    #print("PDF监测线程已启动")
    while True:
        print("PDF监测线程已启动")
        try:
            with app.app_context():
                # 使用现有会话查询病人
                processing_patients = Patient.query.filter_by(status="processing").all()
                if processing_patients:
                    print(f"当前有 {len(processing_patients)} 个病人正在处理中")
                for patient in processing_patients:
                    folder_path = os.path.join(r"C:\Users\admin\Desktop\生物反馈\PatientData", patient.patient_id)
                    if os.path.exists(folder_path):
                        files = os.listdir(folder_path)
                        pdf_files = [f for f in files if f.endswith('.pdf')]
                        if pdf_files:
                            print(f"发现PDF文件：{pdf_files}")
                            try:
                                patient.status = "processed"
                                patient.completed_time = datetime.now()
                                db.session.commit()
                                print(f"病人 {patient.name} 的检查报告已生成")
                            except Exception as db_error:
                                db.session.rollback()
                                print(f"数据库更新错误: {str(db_error)}")
                                
        except Exception as e:
            print(f"监测线程错误: {str(e)}")
            if 'db' in locals():
                db.session.rollback()
        
        time.sleep(5)
# ... 之前添加启动处理线程的代码
# 启动处理线程


@app.route("/verify_doctor", methods=["POST"])
def verify_doctor():
    try:
        data = request.json
        db_id = data.get('patientId')  # 获取数据库ID
        print(f"数据库ID: {db_id}")
        
        # 添加patient_id验证
        if not db_id:
            return jsonify({'success': False, 'message': '未提供病人ID'}), 400
            
        # 获取病人信息
        patient = Patient.query.filter_by(id=db_id).first()
        if not patient:
            return jsonify({'success': False, 'message': '未找到对应的病人信息'}), 404
            
        print(f"病人就诊号: {patient.patient_id}")  # 打印就诊号以便调试

        # 构建验证payload
        payload = {
            "version": "1.0",
            "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
            "signAlgo": "HMAC",
            "idType": "SF"  # 假设这里身份证类型是 SF（身份证）
        }

        # 根据提供的信息类型调用不同的验证方法
        if 'workId' in data:
            # 工号验证
            payload["uniqueId"] = data['workId']  # 使用 workId 作为 uniqueId
        else:
            # 姓名和身份证验证
            payload["idNumber"] = data['idNumber']
        
        # 生成签名
        payload["signature"] = sort_json_by_ascii(payload)

        print(payload)

        # 发起请求
        headers = {
            "Content-Type": "application/json"
        }

        url = 'https://newcoss-dev.isignet.cn:10201/coss/service/v1/queryUserInfo'
        response = requests.post(url, data=json.dumps(payload), headers=headers)


        # 处理响应
        if response.status_code == 200:
            result = response.json()
            print(result)
            if result.get('message') == 'SUCCESS':
                user_id = result.get('data', {}).get('userId')
                print(user_id)
                # 获取PDF文件路径
                
                folder_path = os.path.join(r"C:\Users\admin\Desktop\生物反馈\PatientData", patient.patient_id)
                pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
                if not pdf_files:
                    return jsonify({'success': False, 'message': '未找到PDF文件'}), 404
                    
                pdf_file_path = os.path.join(folder_path, pdf_files[0])
               
                
                #pdf_file_path = os.path.join(r"/Users/michaelwang/Desktop/华西project/TestFile/TestPDF.pdf")

                # 读取PDF文件
                with open(pdf_file_path, "rb") as pdf_file:
                    base64_data = base64.b64encode(pdf_file.read()).decode('utf-8')
                print('pdf get successful')

                # 构建签名请求
                additional_payload = {
                    "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
                    "signAlgo": "HMACSHA256",
                    "signSealType": "BJCA_SM2",
                    "userId": user_id,
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

                additional_payload["signature"] = sort_json_by_ascii(additional_payload)

                # 向另一个服务发送指令
                additional_response = requests.post('https://newcoss-dev.isignet.cn:10201/coss/service/v1/autoPdfSign', json=additional_payload)
                if additional_response.status_code == 200:
                    print('pdf signed: ')
                    sign_result = additional_response.json()
                    signed_pdf = sign_result['data']['composePdf']
                    
                    # 保存签名后的PDF数据到数据库
                    try:
                        patient.signed_pdf = signed_pdf
                        db.session.commit()
                        print(f"已保存病人 {patient.name} 的签名PDF数据")
                        
                        # 构建发送给HIS的XML数据
                        xml_data = f"""
<Request>
    <Header>
        <SourceSystem></SourceSystem>
        <MessageID></MessageID>
    </Header>
    <Body>
        <RegisterDocumentRt>
            <OrganizationCode>{patient.hospital_code or ''}</OrganizationCode>
            <PATPatientID>{patient.patient_id or ''}</PATPatientID>
            <PATPatientName>{patient.name or ''}</PATPatientName>
            <PAADMVisitNumber>{patient.visit_number or ''}</PAADMVisitNumber>
            <RISRExamID></RISRExamID>
            <SpecimenID></SpecimenID>
            <OEORIOrderItemID>{patient.order_item_id or ''}</OEORIOrderItemID>
            <DocumentType></DocumentType>
            <DocumentID></DocumentID>
            <DocumentContent>{signed_pdf}</DocumentContent>
            <DocumentPath></DocumentPath>
            <UpdateUserCode>{patient.update_user_code or ''}</UpdateUserCode>
            <UpdateDate>{datetime.now().strftime('%Y%m%d')}</UpdateDate>
            <UpdateTime>{datetime.now().strftime('%H%M%S')}</UpdateTime>
        </RegisterDocumentRt>
    </Body>
</Request>"""
                        escaped_xml_data = saxutils.escape(xml_data)



                        # 发送XML数据到HIS WebService
                        his_url = 'http://172.21.234.63/csp/hsb/DHC.Published.PUB0018.BS.PUB0018.CLS?WSDL=1'  # 需要替换为实际的HIS WebService地址
                        his_headers = {
                            'Content-Type': 'text/xml;charset=UTF-8',
                            'SOAPAction': 'MES0138'  # 需要根据实际的WebService配置修改
                        }
                        
                        his_response = requests.post(his_url, data=xml_data, headers=his_headers)
                        print(f"HIS响应状态码: {his_response.status_code}")
                        print(f"HIS响应内容: {his_response.text}")
                        
                    except Exception as db_error:
                        db.session.rollback()
                        print(f"保存签名PDF数据或发送HIS数据时出错: {str(db_error)}")
                        return jsonify({'success': False, 'message': '保存签名PDF或发送HIS数据失败'}), 500
                    
                    return jsonify({'success': True, 'message': '自动签字成功'}), 200
                if additional_response.status_code != 200:
                    additional_response = requests.post('https://newcoss-dev.isignet.cn:10201/coss/service/v1/addPdfSignJob', json=additional_payload)
                    if additional_response.status_code == 200:
                        return  jsonify({'success': True, 'message': '签字请求发送成功，等待签字结果'}), 200
                else:
                    return jsonify({'success': False, 'message': '指令发送失败'}), 500
                
        # 如果没有成功的结果
        return jsonify({'success': False, 'message': '医生验证失败'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route("/auto_sign_doctor", methods=["POST"])
def auto_sign_doctor():
    try:
        data = request.json
        db_id = data.get('patientId')
        
        if not db_id:
            return jsonify({'success': False, 'message': '未提供病人ID'}), 400
            
        patient = Patient.query.filter_by(id=db_id).first()
        if not patient:
            return jsonify({'success': False, 'message': '未找到对应的病人信息'}), 404

        # 构建验证payload
        payload = {
            "version": "1.0",
            "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
            "signAlgo": "HMAC",
            "idType": "SF"
        }

        # 根据验证方式设置参数
        if 'workId' in data:
            payload["uniqueId"] = data['workId']
        else:
            payload["idNumber"] = data['idNumber']
        
        payload["signature"] = sort_json_by_ascii(payload)
        print(payload)
        # 发送验证请求并保存验证信息
        url = 'https://newcoss-dev.isignet.cn:10201/coss/service/v1/queryUserInfo'
        response = requests.post(url, json.dumps(payload), headers={"Content-Type": "application/json"})

        if response.status_code == 200:
            result = response.json()
            print(result)
            if result.get('message') == 'SUCCESS':
                print("成功请求医生信息")
                # 保存验证信息用于后续自动签名
                user_id = result['data']['userId']
                print(user_id)

                param = {
                    "version":"1.0",
                    "appId":"APP_7B3F36A14E99410A80B37AEF332E3247",
                    "signAlgo":"HMAC",
                    "userId": user_id,
                    "timeRegion":"1440",
                    "requireQrCode":"Y"
                }
                param["signature"] = sort_json_by_ascii(param)
                auto_sign_url =  'https://newcoss-dev.isignet.cn:10201/coss/service/v1/startAutoSign'
                auto_sign_response = requests.post(auto_sign_url, json.dumps(param), headers={"Content-Type": "application/json"})
                if auto_sign_response.status_code == 200:
                    result = auto_sign_response.json()
                    QRCodeBase64 = result['data']['qrCode']

                    return jsonify({
                        'success': True,
                        'message': '自动签名已开启',
                        'qrCode': QRCodeBase64  # 返回二维码数据
                    })

        return jsonify({'success': False, 'message': '自动签字开启失败'}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
    
'''
@app.route("/verify_doctor", methods=["POST"])
def verify_doctor():
    try:
        data = request.json

        # 固定的请求字段
        payload = {
            "version": "1.0",
            "appId": "APP_7B3F36A14E99410A80B37AEF332E3247",
            "signAlgo": "HMAC",
            "idType": "SF"  # 假设这里身份证类型是 SF（身份证）
        }


        # 根据提供的信息类型调用不同的验证方法
        if 'workId' in data:
            # 工号验证
            payload["uniqueId"] = data['workId']  # 使用 workId 作为 idNumber
            payload["signature"] = sort_json_by_ascii(payload)  # 生成签名
            response = requests.post('https://newcoss-dev.isignet.cn:10201/coss/service/v1/queryUserInfo', json=payload)
        
        else:
            # 姓名和身份证验证
            #payload["name"] = data['name']
            payload["idNumber"] = data['idNumber']
            payload["signature"] = sort_json_by_ascii(payload)  # 生成签名
            response = requests.post('https://newcoss-dev.isignet.cn:10201/coss/service/v1/queryUserInfo', json=payload)

        if response.status_code == 200:
            result = response.json()

            user_id = result.get('data', {}).get('userId')

            if result.get('success'):
                return jsonify({
                    'success': True,
                    'userId': result.get('data', {}).get('userId')
                })
        
        return jsonify({'success': False, 'message': '医生验证失败'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
'''
if __name__ == "__main__":
    # 启动监测线程
    monitor_thread = threading.Thread(target=monitor_processed_patients, daemon=True)
    monitor_thread.start()
    
    # 启动处理线程
    process_thread = threading.Thread(target=process_queue, daemon=True)
    process_thread.start()
    
    app.run(debug=True)
