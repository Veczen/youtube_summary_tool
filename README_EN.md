# YouTube Video Monitor & AI Summary System

[中文](./README.md) | **English**

Automatically monitor YouTube channel updates, generate Chinese video summaries using AI, and send email notifications to subscribers.

## ✨ Core Features

- 🔍 **Auto Monitoring**: Hourly automatic detection of new YouTube videos
- 🌐 **Smart Subtitles**: Automatically fetch original language subtitles (English/Japanese/Korean, etc.)
- 🤖 **AI Summary**: Generate structured Chinese content outlines using Gemini AI
- 📧 **Email Push**: Send beautiful HTML format email notifications
- ⏰ **24/7 Running**: GitHub Actions runs automatically 24 hours a day
- 💰 **Completely Free**: All services use free API quotas

## 🚀 5-Minute Quick Deploy

### Step 1: Get API Keys (3 minutes)

| Service | Get From | Description | Free Quota |
|---------|----------|-------------|------------|
| **YouTube API** | [Google Cloud Console](https://console.cloud.google.com/) | Enable YouTube Data API v3 → Create API Key | 10,000 units/day |
| **Gemini AI** | [Google AI Studio](https://makersuite.google.com/app/apikey) | Click "Create API Key" | 15 requests/min |
| **Resend** | [resend.com](https://resend.com/api-keys) | Register → Create API Key | 100 emails/day |

### Step 2: Deploy to GitHub (2 minutes)

1. **Fork this repository** - Click the Fork button in the upper right corner

2. **Configure Secrets** - Go to your repository `Settings` → `Secrets and variables` → `Actions`, add the following 5 secrets:
   
   **API Keys (Required):**
   - `YOUTUBE_API_KEY` - Your YouTube API key
   - `GEMINI_API_KEY` - Your Gemini API key
   - `RESEND_API_KEY` - Your Resend API key
   
   **Email Configuration (Required):**
   - `EMAIL_FROM` - Sender address, format: `YouTube Monitor <onboarding@resend.dev>`
   - `EMAIL_SUBSCRIBERS` - Subscriber emails, comma-separated: `user1@gmail.com,user2@outlook.com`

3. **Modify Configuration** - Edit `config.json` file (only configure channels to monitor):

```json
{
  "channels": [
    {
      "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
      "name": "Google Developers"
    }
  ],
  "check_hours": 24
}
```

**How to get YouTube Channel ID:**
- Visit YouTube channel page, the `UC_x5XG1OV2P6uZZ5FSM9Ttw` in URL is the channel ID
- Or right-click to view page source, search for `"channelId"`

**Email Configuration:**
- ⚠️ **Important**: Email configuration (sender and subscribers) has been moved to GitHub Secrets
- 📖 For detailed configuration: [GitHub Secrets Configuration Guide](./SECRETS_GUIDE.md)
- Do not configure email information in `config.json`

4. **Enable Actions** - Go to `Actions` tab → Enable workflow → Done!

The system will automatically check YouTube updates hourly and send email notifications.

## 📋 Configuration Details

### config.json Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channels` | Array | ✅ | List of YouTube channels to monitor |
| `channels[].id` | String | ✅ | YouTube channel ID (starts with UC) |
| `channels[].name` | String | ✅ | Channel display name (for email title) |
| `check_hours` | Number | ❌ | Check videos from last N hours (default 24) |

**Note**: `subscribers` and `email.from` have been moved to GitHub Secrets configuration

### GitHub Secrets Configuration

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `EMAIL_FROM` | Sender address | `YouTube Monitor <onboarding@resend.dev>` |
| `EMAIL_SUBSCRIBERS` | Subscriber emails (comma-separated) | `user1@gmail.com,user2@outlook.com` |

Detailed configuration: 📖 [GitHub Secrets Configuration Guide](./SECRETS_GUIDE.md)

### Multi-Channel Configuration

```json
{
  "channels": [
    {"id": "UC_x5XG1OV2P6uZZ5FSM9Ttw", "name": "Google Developers"},
    {"id": "UCXuqSBlHAE6Xw-yeJA0Tunw", "name": "Linus Tech Tips"},
    {"id": "UCsooa4yRKGN_zEE8iknghZA", "name": "TED-Ed"}
  ],
  "check_hours": 24
}
```

## 🔧 Local Testing

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Environment Variables

**Windows PowerShell:**
```powershell
$env:YOUTUBE_API_KEY="your_api_key"
$env:GEMINI_API_KEY="your_api_key"
$env:RESEND_API_KEY="your_api_key"
$env:EMAIL_FROM="YouTube Monitor <onboarding@resend.dev>"
$env:EMAIL_SUBSCRIBERS="your-email@example.com"
```

**Linux/Mac:**
```bash
export YOUTUBE_API_KEY="your_api_key"
export GEMINI_API_KEY="your_api_key"
export RESEND_API_KEY="your_api_key"
export EMAIL_FROM="YouTube Monitor <onboarding@resend.dev>"
export EMAIL_SUBSCRIBERS="your-email@example.com"
```

**Multiple Subscribers:**
```powershell
$env:EMAIL_SUBSCRIBERS="user1@gmail.com,user2@outlook.com"
```

### Verify Configuration (Recommended)

```bash
python test_config.py
```

This will verify if all API keys and configuration files are correct.

### Run Program

```bash
python monitor.py
```

**Note:** The program exits automatically after one run. Scheduled execution is handled by GitHub Actions.

## ⚙️ Customize Running Frequency

Edit `.github/workflows/monitor.yml` to modify the cron expression:

```yaml
schedule:
  - cron: '0 * * * *'      # Every hour
  # - cron: '0 */2 * * *'  # Every 2 hours
  # - cron: '0 */6 * * *'  # Every 6 hours  
  # - cron: '0 9,21 * * *' # Daily at 9am and 9pm
```

## 💡 Workflow

```
GitHub Actions (Hourly Trigger)
    ↓
Check YouTube channels for new videos
    ↓
Auto-fetch original language subtitles (EN/JP/KR/CN, etc.)
    ↓
Gemini AI generates Chinese summary
    ↓
Send HTML format email
    ↓
Save state to Git repository
    ↓
Program exits, wait for next trigger
```

**Special Features:**
- 🌐 **Smart Language Detection**: Automatically identify video's original language, prioritize manual subtitles
- 🎨 **Beautiful Emails**: HTML format, responsive design, mobile-friendly
- 💾 **State Persistence**: Record to Git repository, avoid duplicate notifications
- 🔄 **Auto Deduplication**: Processed videos won't be sent again

## 📈 Resource Usage Estimation

| Channels | Frequency | Monthly Minutes | Actions Quota |
|----------|-----------|-----------------|---------------|
| 10 | Hourly | ~360 min | 18% |
| 30 | Hourly | ~540 min | 27% |
| 50 | Every 2hrs | ~360 min | 18% |

All scenarios are well below the 2,000 minutes free quota!

## ⚠️ Important Notes

- ✅ **First Run**: Checks videos from last 24 hours, then only detects new videos
- ✅ **Subtitle Support**: Auto-fetch original language subtitles (EN/JP/KR/ES/CN, etc.)
- ✅ **Email Quota**: Resend free tier offers 100 emails/day, sufficient for personal use
- ⚠️ **Test Email**: Using `onboarding@resend.dev` can only send to verified emails
- ⚠️ **API Limits**: YouTube API offers 10,000 units/day, no pressure for monitoring 100 channels

## 🐛 FAQ

<details>
<summary><b>Q: GitHub Actions not running automatically?</b></summary>

A: 
1. Check if the workflow is enabled on the Actions page
2. Confirm all GitHub Secrets are correctly configured
3. Check the Actions page run logs for errors
</details>

<details>
<summary><b>Q: GitHub Actions permission error (403)?</b></summary>

A:
This is because the workflow doesn't have write permissions. Fixed in latest version, if still having issues:

1. Go to repository `Settings` → `Actions` → `General`
2. Find "Workflow permissions"
3. Select "Read and write permissions"
4. Save settings
5. Re-run workflow
</details>

<details>
<summary><b>Q: Not receiving emails?</b></summary>

A:
1. Check if RESEND_API_KEY is correct
2. When using test email, ensure recipient is verified in Resend account
3. Check spam folder
4. Recommend configuring and verifying your own domain
</details>

<details>
<summary><b>Q: Cannot fetch subtitles?</b></summary>

A:
1. Confirm video has available subtitles (manual or auto-generated)
2. Some videos may have subtitle download disabled
3. System will automatically skip and note in email
</details>

<details>
<summary><b>Q: Want to monitor more channels?</b></summary>

A:
- Theoretically unlimited
- Recommend not exceeding 100 channels (API quota consideration)
- Can adjust `check_hours` parameter to reduce API calls
</details>

## 📝 Project Files

```
gpt_information_summary/
├── monitor.py              # Main program
├── test_config.py          # Configuration validation script
├── config.json             # User configuration file
├── config.example.json     # Configuration example
├── last_videos.json        # State record (auto-generated)
├── requirements.txt        # Python dependencies
├── README.md              # Chinese documentation
├── README_EN.md           # This document
└── .github/workflows/
    └── monitor.yml        # GitHub Actions configuration
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

If you have questions or suggestions, please submit them on the [Issues](../../issues) page.

## 📄 License

MIT License - Free to use and modify

---

**🎉 Start monitoring your favorite YouTube channels now!**

