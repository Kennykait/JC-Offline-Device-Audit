# JumpCloud & HiBob Audit Automation

This repository contains **automated scripts** for auditing JumpCloud device assignments, retrieving user vacation statuses from HiBob, and generating a formatted **Google Sheets report**. The scripts are designed to be **run via Jenkins** and integrate with **Slack notifications**.

## **📌 Features**
- **🔗 JumpCloud Device Audit**: Fetches all inactive devices and user assignments.
- **🛑 HiBob Vacation Status**: Checks if employees are on vacation.
- **📊 Google Sheets Report**: Generates a fully formatted Google Sheet with:
  - Locked header row
  - Conditional formatting (e.g., **red for suspended accounts**)
  - Auto-sized columns
  - Hyperlinks for **JumpCloud Device IDs** and **User IDs**
- **🔔 Slack Integration**: Sends notifications before and after execution.

---

## **📌 Scripts**
### **1️⃣ `JumpCloudAudit.ps1`** (Main PowerShell Script)
Runs the **JumpCloud audit**, fetches **ignore lists**, and triggers the **Python scripts**.

### **2️⃣ `GoogleSheetsUploader.py`** (Python)
Uploads the audit results to **Google Sheets**, applying formatting and hyperlinks.

### **3️⃣ `HiBobFetcher.py`** (Python)
Retrieves **vacation statuses** from **HiBob** for each user in the audit.

### **4️⃣ `GoogleSheetsIgnoreFetcher.py`** (Python)
Fetches the **ignore list** from a dedicated **Google Sheets tab**.

---

## **📌 Setup**
### **1️⃣ Requirements**
- Python `>=3.10`
- PowerShell `>=7`
- **Google Sheets API Credentials**
  - Store the JSON key file at:
    ```
    C:\Scripts\NordSec\Audit\service_account.json
    ```

### **2️⃣ Install Dependencies**
Run:
```powershell
pip install -r requirements.txt
