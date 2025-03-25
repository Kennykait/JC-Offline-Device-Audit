# JumpCloud & HiBob Audit Automation

This branch should be used only for Jenkins. For script usage see the main branch.

## 🔧 Jenkins Pipeline Setup

### Required Jenkins Credentials:
| ID                     | Description                    |
|------------------------|--------------------------------|
| `google-sheet-id`      | Google Sheets doc ID           |
| `jumpcloud-api-key`    | JumpCloud API Key              |
| `slack-webhook-url`    | Slack Incoming Webhook URL     |
| `HIBOB_SERVICE_USER_ID`| HiBob service account ID       |
| `HIBOB_API_TOKEN`      | HiBob service account token    |

### Required Environment Variables:
| Name             | Example Value                    |
|------------------|----------------------------------|
| `IGNORE_TAB_NAME`| Ignore List                      |
| `SLACK_MESSAGE`  | JumpCloud Offline Audit Completed |
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

### Trigger via Jenkins:
```groovy
powershell.exe -ExecutionPolicy Bypass -File C:\Scripts\NordSec\Audit\powershell\RunJumpCloudAudit.ps1
