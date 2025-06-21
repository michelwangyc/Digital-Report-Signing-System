import requests
xml_data_new = """
<Request><Header><SourceSystem>02</SourceSystem><MessageID>598205</MessageID></Header><Body><UpdateOrdersRt><BusinessFieldCode>00001</BusinessFieldCode><HospitalCode>F0001</HospitalCode><PATPatientID>0037216733</PATPatientID><PAADMVisitNumber>178687042</PAADMVisitNumber><PAADMEncounterTypeCode>I</PAADMEncounterTypeCode><OEORIInfoList><OEORIInfo><BusinessFieldCode>00001</BusinessFieldCode><HospitalCode></HospitalCode><OEORIOrderItemID>175923714||3125</OEORIOrderItemID><OEORIStatusCode>C</OEORIStatusCode><OEORIOrdSubCatCode>0223</OEORIOrdSubCatCode><OEORIOrdSubCatDesc>心理评估与治疗</OEORIOrdSubCatDesc><OEORIOrdCatCode>02</OEORIOrdCatCode><OEORIOrdCatDesc>治疗</OEORIOrdCatDesc><OEORIParentOrderID></OEORIParentOrderID><OEORIExecDeptCode>7820</OEORIExecDeptCode><OEORIExecDeptDesc>心理卫生中心医疗单元</OEORIExecDeptDesc><OEORIStopDoc>36358</OEORIStopDoc><OEORIStopDocDesc>郭子瑜</OEORIStopDocDesc><OEORIFeeType>INSUXYB</OEORIFeeType><OEORIServMethod></OEORIServMethod><OEORIArcim>20406||1</OEORIArcim></OEORIInfo></OEORIInfoList><UpdateUserCode>demo</UpdateUserCode><UpdateUserDesc>demo</UpdateUserDesc><UpdateDate>2025-05-14</UpdateDate><UpdateTime>14:34:42</UpdateTime></UpdateOrdersRt></Body></Request>
"""
# 构造发送的 XML 数据
xml_data = """<Request>
  <Header>
    <SourceSystem>02</SourceSystem>
    <MessageID>589330</MessageID>
  </Header>
  <Body>
    <UpdateOrdersRt>
      <BusinessFieldCode>00001</BusinessFieldCode>
      <HospitalCode>F0001</HospitalCode>
      <PATPatientID>0037216733</PATPatientID>
      <PAADMVisitNumber>178687042</PAADMVisitNumber>
      <PAADMEncounterTypeCode>I</PAADMEncounterTypeCode>
      <OEORIInfoList>
        <OEORIInfo>
          <BusinessFieldCode>00001</BusinessFieldCode>
          <HospitalCode/>
          <OEORIOrderItemID>175923714||1670</OEORIOrderItemID>
          <OEORIStatusCode>C</OEORIStatusCode>
          <OEORIOrdSubCatCode>80</OEORIOrdSubCatCode>
          <OEORIOrdSubCatDesc>专科检查</OEORIOrdSubCatDesc>
          <OEORIOrdCatCode>03</OEORIOrdCatCode>
          <OEORIOrdCatDesc>检查</OEORIOrdCatDesc>
          <OEORIParentOrderID/>
          <OEORIExecDeptCode>4185</OEORIExecDeptCode>
          <OEORIExecDeptDesc>临床营养科</OEORIExecDeptDesc>
          <OEORIStopDoc>ys001</OEORIStopDoc>
          <OEORIStopDocDesc>测试医生3</OEORIStopDocDesc>
          <OEORIFeeType>01</OEORIFeeType>
          <OEORIServMethod>S</OEORIServMethod>
          <OEORIArcim>20186||1</OEORIArcim>
        </OEORIInfo>
      </OEORIInfoList>
      <UpdateUserCode>demo</UpdateUserCode>
      <UpdateUserDesc>demo</UpdateUserDesc>
      <UpdateDate>2024-10-17</UpdateDate>
      <UpdateTime>16:37:36</UpdateTime>
    </UpdateOrdersRt>
  </Body>
</Request>"""

# 发送 POST 请求
response = requests.post("http://127.0.0.1:5000/his/patient_info", data=xml_data_new, headers={"Content-Type": "application/xml"})

# 打印返回的响应内容
print(response.text)