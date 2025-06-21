# Digital-Report-Signing-System
Developed a paperless medical reporting platform for West China Hospital’s Mental Health Center, integrating HIS, biofeedback systems, and CA digital signatures. Enabled real-time data flow, automated report generation/signing, and reduced patient testing procedures by over 30%.


This system is a paperless platform developed for the Mental Health Center of West China Hospital, primarily serving as an integration bridge for autonomic nervous system stability testing with the Hospital Information System (HIS). The core business workflow is as follows:

1. Patient Information Processing Workflow

The system categorizes patients into the following statuses:
	•	Pending: Initial state, patients awaiting processing
	•	Processing: Patients whose information has been sent to the biofeedback system for testing
	•	Processed: Testing completed, PDF report generated, awaiting doctor’s signature
	•	Sent: Doctor has signed the report, and it has been sent back to the HIS system

2. Core Functional Modules

2.1 HIS Information Receiving Module
	•	Receives patient information from the HIS system via XML interface
	•	Supports multiple message types: AddRisAppBillRt, UpdateOrdersRt, RisRegistry, etc.
	•	Utilizes a message queue to handle incoming messages asynchronously

2.2 Patient Information Management Module
	•	Stores and manages patient demographic data, visit details, and test information
	•	Provides a web interface displaying patients in different statuses
	•	Supports detailed patient data viewing

2.3 Biofeedback System Integration Module
	•	Sends patient information to the biofeedback system (Access database)
	•	Creates a folder for each patient to store test results
	•	Monitors the generation of PDF reports

2.4 Electronic Signature Module
	•	Integrates with the CA digital signature system
	•	Supports physician identity verification
	•	Enables automatic PDF report signing
	•	Sends signed reports back to the HIS system

⸻

System Deployment Architecture

1. Server Components
	•	Web Application Server: Runs the Flask app, provides web UI and API interfaces
	•	Database Server: Stores patient data and status using SQLite
	•	File Storage System: Stores PDF reports

2. External System Integrations
	•	HIS System: Integrated via WebService interface
	•	Biofeedback System: Integrated via Access database (MultiTrace.mdb)
	•	CA Signature System: Integrated via REST API (newcoss-dev.isignet.cn)

3. Data Flow
	1.	HIS → Paperless Platform: Patient demographics and visit info
	2.	Platform → Biofeedback System: Patient data
	3.	Biofeedback System → Platform: Test results (PDF report)
	4.	Platform → CA System: Report signature request
	5.	CA System → Platform: Signed PDF report
	6.	Platform → HIS: Final signed report

4. Technical Architecture
	•	Backend: Python with Flask framework
	•	Frontend: HTML, Bootstrap 3, JavaScript
	•	Database: SQLite
	•	Protocols: HTTP/HTTPS, SOAP (WebService)
	•	Data Formats: XML, JSON
	•	Background Tasks: Multithreading (for monitoring PDF generation and message queue processing)

⸻

System Highlights
	1.	Paperless Workflow: End-to-end electronic process from patient data reception to report signing and archiving
	2.	Multi-System Integration: HIS, biofeedback system, and CA signature system
	3.	Asynchronous Processing: Uses message queues and multithreaded task handling
	4.	Status Monitoring: Automatically tracks patient status and reports generation
	5.	Secure Authentication: Supports physician verification and digital signing

This system achieves a fully paperless workflow covering patient data reception, test execution, report generation, signing, and archiving, significantly improving the efficiency and data management capability of the mental health center.


# Steps to run the program
1. In the terminal, input the following command: 
pip install -r requirements.txt

2. Run main.py and copy the IP address displayed in the terminal.
3. In the VirtualServer folder, run the py files to receive and update patient info.
