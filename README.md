# JumpCloud Offline Device Audit (Jenkins-Optimized)

This project performs a full audit of JumpCloud systems to identify inactive devices, user binding status, and vacation information pulled from HiBob. The results are formatted and uploaded to Google Sheets and shared via Slack.
NOTE : This branch should be used only for Jenkins. For script usage see the main branch.

---

## 🔧 Features

- Detects inactive JumpCloud devices (offline >16 days)
- Gathers bound user info (email, status, user ID)
- Integrates HiBob time off data
- Google Sheets report with formatting
- Slack notifications with report link
- Jenkins pipeline ready

---

## 🔧 Jenkins Pipeline Setup

---

## 🔐 Jenkins Credentials

Add these in **Jenkins → Manage Jenkins → Credentials**:

| ID                       | Type          | Description                              |
|--------------------------|---------------|------------------------------------------|
| `google-sheet-id`        | Secret Text   | Your Google Sheet ID                     |
| `google-service-account` | Secret File   | Your service_account.json file           |
| `jumpcloud-api-key`      | Secret Text   | JumpCloud API Key                        |
| `slack-webhook-url`      | Secret Text   | Slack webhook URL                        |
| `HIBOB_SERVICE_USER_ID`  | Secret Text   | HiBob Service User ID                    |
| `HIBOB_API_TOKEN`        | Secret Text   | HiBob API Token                          |

### Required Environment Variables:
| Name             | Example Value                    |
|------------------|----------------------------------|
| `IGNORE_TAB_NAME`| Ignore List                      |
| `SLACK_MESSAGE`  | JumpCloud Offline Audit Completed|
| `SLACK_TAGS`     | <@jumpcloud_team>                |

---

### Jenkinsfile Summary:
- Stage 1: Checkout code
- Stage 2: Install dependencies
- Stage 3: Fetch Google Sheet ignore list
- Stage 4: Run PowerShell audit script
- Stage 5: Fetch HiBob vacation status
- Stage 6: Upload final report to Google Sheets
- Final Step: Notify via Slack

---

## 📌 Notes

- The service account file is handled securely via Jenkins **Secret File** credential.
- Python scripts support command-line arguments for Jenkins compatibility.
- The `GoogleSheetsUploader.py` script accepts `--creds` argument to specify injected file path.

---