# JumpCloud & HiBob Audit Automation

This is a project i worked on for quite a while since doing device reports and audits took a long time and would require input from different systems on the state of the device and user. I've connected the three core systems our business uses - JumpCloud, HiBob and GWS. Each of the system servers a purpose :
JumpCloud - Device status
HiBob - Users Status
GWS - Handling the Data

In theory you could use this script if your'e only using JumpCloud since the script stores the information in json format. You could potentially create a script with a different HRIS or Office product to handle the jsons and then use the ps1.

This repository contains **automated scripts** for:
- **🔗 JumpCloud Device Audit**: Fetches all inactive devices and user assignments.
- **🛑 HiBob Vacation Status**: Checks if employees are on vacation.
- **📊 Google Sheets Report**: Generates a fully formatted Google Sheet with:
  - Locked header row
  - Conditional formatting (e.g., **red for suspended accounts**)
  - Auto-sized columns
  - Hyperlinks for **JumpCloud Device IDs** and **User IDs**
- **🔔 Slack Integration**: Sends notifications before and after execution.

## **📌 Configuration Variables**
Before running the script, update the variables inside **`JumpCloudAudit.ps1`**.

### **1️⃣ Required Variables**
| Variable | Description |
|----------|-------------|
| `$APIKey` | **JumpCloud API Key** – [How to get it](https://jumpcloud.com/api-key) |
| `$GoogleSheetID` | **Google Sheet ID** for storing the report |
| `$GoogleSheetIgnoreTab` | **Tab name** in Google Sheets containing ignored devices |
| `$CSVOutput` | **Path to store CSV reports** locally |
| `$LogFilePath` | **Path for logging** the script execution |
| `$IgnoreListPath` | **Path to store the ignore list JSON file** |
| `$PythonExecutable` | **Path to Python 3 executable** (`python.exe`) |
| `$GoogleSheetsUploader` | **Path to** `GoogleSheetsUploader.py` |
| `$HiBobFetcher` | **Path to** `HiBobFetcher.py` |
| `$GoogleSheetsIgnoreFetcher` | **Path to** `GoogleSheetsIgnoreFetcher.py` |
| `$SlackWebhookURL` | **Slack Webhook URL** – [Set it up here](https://api.slack.com/messaging/webhooks) |
| `$SlackChannel` | **Slack channel** where notifications should be sent |

---

## **📌 Setup Guide**
### **1️⃣ Google Cloud Service Account (Google Sheets API)**
#### **Step 1: Enable Google Sheets API**
1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**
2. Click on **"Select a project"**, then **"New Project"**.
3. Search for **"Google Sheets API"** and enable it.

#### **Step 2: Create a Service Account**
1. Go to **[Google IAM & Admin](https://console.cloud.google.com/iam-admin/serviceaccounts)**
2. Click **"Create Service Account"**.
3. Set a name (e.g., `jumpcloud-audit`).
4. Assign **"Editor"** or **"Owner"** role.
5. Click **"Create Key"** → Choose **JSON** → Download the key file.

#### **Step 3: Grant Access to Google Sheets (Two Methods)**

🔹 **Method 1 (Recommended)**: **Share an existing Google Sheet with the service account**
1. Open **your Google Sheet**.
2. Share it with **the service account email** (e.g., `your-service-account@your-project.iam.gserviceaccount.com`).
3. Give **Editor** permissions.

🔹 **Method 2 (Alternative for restricted organizations)**: **Create the Google Sheet using the Service Account**
Some organizations might have locked down the functionality to invite non-gmail accounts to Sheets. This blocks the service account from accessing and populating the Sheet. What we will do is create the Sheet and give ourselves owner rights :
1. Open the included "CreateSheet.py" python script
2. Populate the required variables and don't forget to enter your email to give yourself ownership
3. Run the script
4. You should receive an email with a invitation to the Spreadsheet and the console output will give you the Sheet ID as well.

#### **Step 4: Populate Variables**
Now that we have the bulk of required variables we can populate them and run the script in pwsh or use Jenkins to automate the job.
For Jenkins i recommend using a Freestyle project with a 30 minute timeout (Depending on the size of your organization)
