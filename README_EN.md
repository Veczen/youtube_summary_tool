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

### GitHub Secrets Detailed Configuration

#### Required Secrets (7 in total)

| Secret Name | Description | Example | How to Get |
|-------------|-------------|---------|-----------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | `AIzaSyC...` | [Google Cloud Console](https://console.cloud.google.com/) |
| `GEMINI_API_KEY` | Google Gemini AI key | `AIzaSyD...` | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `RESEND_API_KEY` | Resend email service key | `re_...` | [Resend Dashboard](https://resend.com/api-keys) |
| `EMAIL_FROM` | Sender address | `YouTube Monitor <onboarding@resend.dev>` | Verify domain in Resend or use test domain |
| `EMAIL_SUBSCRIBERS` | Subscriber emails (comma-separated) | `user1@gmail.com,user2@gmail.com` | Your email addresses |
| `AZURE_SPEECH_KEY` | Azure Speech service key (Optional) | `abc123...` | [Azure Portal](https://portal.azure.com/) |
| `AZURE_SPEECH_REGION` | Azure service region (Optional) | `eastus` | Azure Speech service location/region |

#### Configuration Steps

1. Go to your forked repository
2. Click `Settings` → `Secrets and variables` → `Actions`
3. Click `New repository secret`
4. Enter the Secret name and value from the table above
5. Click `Add secret`
6. Repeat steps 3-5 to add all 7 Secrets

#### Free Tier Quotas

| Service | Free Quota | Sufficient For |
|---------|-----------|----------------|
| YouTube Data API | 10,000 units/day | Monitor 100+ channels |
| Gemini AI | 15 requests/min | Process multiple videos per hour |
| Resend | 100 emails/day or 3,000/month | Personal use |
| Azure Speech | 5 hours/month | Process ~30 videos without subtitles |
| GitHub Actions | 2,000 min/month (unlimited for public repos) | Run 24/7 |

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
Try to fetch video subtitles (prioritize original language)
    ↓
Subtitles available? ─── No ──→ Download audio via 3rd-party API → Azure Speech to text
    ↓ Yes
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
- 🔊 **Audio Transcription Backup**: When subtitles unavailable, auto-download audio via 3rd-party API and transcribe (no cookies needed)
- 🎨 **Beautiful Emails**: HTML format, responsive design, mobile-friendly
- 💾 **State Persistence**: Record to Git repository, avoid duplicate notifications
- 🔄 **Auto Deduplication**: Processed videos won't be sent again
- 🛡️ **Bypass IP Restrictions**: Use 3rd-party API for audio download, no worry about GitHub Actions IP blocking

## 📈 Resource Usage Estimation

| Channels | Frequency | Monthly Minutes | Actions Quota |
|----------|-----------|-----------------|---------------|
| 10 | Hourly | ~360 min | 18% |
| 30 | Hourly | ~540 min | 27% |
| 50 | Every 2hrs | ~360 min | 18% |

All scenarios are well below the 2,000 minutes free quota!

## ⚠️ Important Notes

### Feature Description
- ✅ **First Run**: Checks videos from last 24 hours, then only detects new videos
- ✅ **Subtitle Priority**: Auto-fetch original language subtitles (EN/JP/KR/ES/CN, etc.)
- 🔊 **Audio Backup**: When subtitles disabled, auto-download audio and transcribe (requires Azure Speech)
- 🛡️ **Bypass IP Blocking**: Use 3rd-party API for audio download, no worry about GitHub Actions IP restrictions

### Cost Control
- ⚠️ **Azure Optional**: Most YouTube videos have subtitles, Azure Speech is only a fallback
- 💰 **Free Quota**: Azure offers 5 hours/month free, can skip if all monitored channels have subtitles
- ✅ **Email Quota**: Resend free tier offers 100 emails/day, sufficient for personal use

### Configuration Tips
- ⚠️ **Test Email Limitation**: `onboarding@resend.dev` can only send to verified emails
- 💡 **Recommended**: Configure and verify your own domain in Resend for higher quota
- ⚠️ **API Limits**: YouTube API offers 10,000 units/day, no pressure for 100 channels

### Privacy Protection
- 🔒 **Sensitive Info**: All API keys and email configs are in GitHub Secrets
- ✅ **Secure Storage**: Secrets are encrypted, not exposed in code or logs
- 👥 **Multi-user Friendly**: Each user sets their own Secrets after forking

### Audio Transcription Flow (when subtitles unavailable)
1. Download MP3 audio using 3rd-party API (ytb2mp3.xyz)
2. Convert MP3 → WAV using FFmpeg
3. Azure Speech SDK performs speech recognition (supports Chinese/English/Japanese/Korean)
4. Return text for AI summarization

**Advantage**: Completely bypass YouTube IP detection, no cookies needed

## 🐛 FAQ

<details>
<summary><b>Q: GitHub Actions not running automatically?</b></summary>

A: 
1. Check if the workflow is enabled on the Actions page
2. Confirm all GitHub Secrets are correctly configured
3. Check the Actions page run logs for errors
4. After first Fork, manually trigger once or wait for scheduled task
</details>

<details>
<summary><b>Q: GitHub Actions permission error (403)?</b></summary>

A:
This is because the workflow doesn't have write permissions to commit `last_videos.json` state file.

**Solution:**
1. Go to repository `Settings` → `Actions` → `General`
2. Find "Workflow permissions"
3. Select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"** (optional)
5. Click Save
6. Re-run workflow

**Note**: This permission is only used to update `last_videos.json` file to avoid duplicate notifications.
</details>

<details>
<summary><b>Q: FFmpeg installation failed?</b></summary>

A:
If you see FFmpeg-related errors, confirm `.github/workflows/monitor.yml` contains:

```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y ffmpeg
```

Latest version already includes this step, just pull the latest code.
</details>

<details>
<summary><b>Q: Not receiving emails?</b></summary>

A:
1. **Check API Key**: Confirm `RESEND_API_KEY` is correct
2. **Verify Email**: When using `onboarding@resend.dev`, add and verify recipient email in Resend dashboard
3. **Check Spam**: Emails might be marked as spam
4. **Domain Verification**: Recommend configuring and verifying your own domain in Resend
5. **Quota Limit**: Free tier limits to 100 emails/day

**Recommended Solution**:
- Configure and verify your own domain
- Use reliable email services like Gmail/Outlook for receiving
</details>

<details>
<summary><b>Q: Cannot fetch subtitles?</b></summary>

A:
1. Confirm video has available subtitles (manual or auto-generated)
2. Some videos have subtitle download disabled
3. If Azure Speech is configured, system will auto-download audio and transcribe
4. System will note subtitle fetch status in email
</details>

<details>
<summary><b>Q: Azure Speech transcription failed?</b></summary>

A:
1. Confirm `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` are correct
2. Check Azure service region format (lowercase, e.g., `eastus`, `westus2`)
3. Confirm Azure free quota not exhausted (5 hours/month)
4. Check detailed error info in Actions logs

**Note**: Azure Speech only activates when subtitles unavailable. Most videos have subtitles, so this is optional.
</details>

<details>
<summary><b>Q: YouTube download blocked?</b></summary>

A:
System already uses 3rd-party API (ytb2mp3.xyz) to bypass YouTube IP restrictions:
- ✅ No cookies configuration needed
- ✅ Works in GitHub Actions
- ✅ Auto-handles audio download

If 3rd-party API unavailable, system will skip that video and note in email.
</details>

<details>
<summary><b>Q: Want to monitor more channels?</b></summary>

A:
- Theoretically unlimited
- Recommend not exceeding 100 channels (API quota consideration)
- Can adjust `check_hours` parameter to reduce API calls
- YouTube API's 10,000 units/day quota is sufficient for monitoring many channels
</details>

<details>
<summary><b>Q: How to protect privacy? Don't want email exposed in public repo?</b></summary>

A:
✅ Already solved! All sensitive info stored in GitHub Secrets:
- Email config not in `config.json`
- All API keys encrypted
- Each user sets own Secrets after forking
- No private info visible in public repo

**Config Location**: `Settings` → `Secrets and variables` → `Actions`
</details>

<details>
<summary><b>Q: How to manually trigger test?</b></summary>

A:
1. Go to repository's `Actions` tab
2. Select `YouTube Monitor` workflow
3. Click `Run workflow` button
4. Select branch (usually main)
5. Click green `Run workflow` to confirm
6. Wait a few minutes to check results
</details>

## 📝 Project Files

```
gpt_information_summary/
├── monitor.py              # Main program
├── config.json             # User configuration file
├── last_videos.json        # State record (auto-generated)
├── requirements.txt        # Python dependencies
├── README.md              # Chinese documentation
├── README_EN.md           # This document
├── test_audio_download.py  # Audio download test script
├── test_full_pipeline.py   # Full pipeline test script
└── .github/workflows/
    └── monitor.yml        # GitHub Actions configuration
```

## 🏗️ Technical Architecture

### Core Tech Stack
- **Language**: Python 3.11+
- **YouTube API**: Google YouTube Data API v3
- **AI Model**: Google Gemini 2.5 Flash
- **Email Service**: Resend API
- **Speech Recognition**: Azure Cognitive Services Speech SDK
- **Subtitle Fetching**: youtube-transcript-api
- **Audio Download**: 3rd-party API (ytb2mp3.xyz)
- **Audio Processing**: FFmpeg
- **CI/CD**: GitHub Actions

### System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│               GitHub Actions Scheduled Trigger                │
│                     (Runs Every Hour)                         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
        ┌────────────────────────────┐
        │   YouTube Data API v3      │
        │  Get Latest Channel Videos │
        └────────────┬───────────────┘
                     ↓
        ┌────────────────────────────┐
        │  Check last_videos.json    │
        │  Filter Processed Videos   │
        └────────────┬───────────────┘
                     ↓
        ┌────────────────────────────┐
        │  Try to Fetch Subtitles    │
        │ (youtube-transcript-api)   │
        └────────┬────────────┬──────┘
                 │            │
    Subtitles OK │            │ No Subtitles
                 ↓            ↓
        ┌────────────┐  ┌──────────────────┐
        │Extract Text│  │ Download Audio    │
        └─────┬──────┘  │ (ytb2mp3.xyz API)│
              │         └────────┬─────────┘
              │                  ↓
              │         ┌──────────────────┐
              │         │ FFmpeg Convert   │
              │         │  (MP3 → WAV)     │
              │         └────────┬─────────┘
              │                  ↓
              │         ┌──────────────────┐
              │         │ Azure Speech SDK │
              │         │ Speech-to-Text   │
              │         └────────┬─────────┘
              │                  │
              └──────────┬───────┘
                         ↓
              ┌──────────────────────┐
              │ Gemini AI Generate   │
              │  Summary (Chinese)   │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │  Resend API Send     │
              │   Email (HTML)       │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │Update last_videos.json│
              │ (Git commit & push)  │
              └──────────────────────┘
```

### Key Design Decisions

1. **Subtitle Priority**: Use subtitles first to reduce Azure Speech quota usage
2. **3rd-party Audio Download**: Bypass YouTube IP restrictions without cookies
3. **Environment Variables**: Store sensitive info in GitHub Secrets for privacy
4. **State Persistence**: Use Git repository to store state, avoid duplicate notifications
5. **HTML Email**: Better reading experience with mobile support

## 📅 Changelog

### v2.0 (2025-11-27)
- ✅ Added audio transcription (Azure Speech)
- ✅ Use 3rd-party API for audio download, bypass IP restrictions
- ✅ Support multi-language subtitle auto-detection
- ✅ Optimized HTML email format
- ✅ Privacy protection: moved sensitive info to GitHub Secrets

### v1.0 (2025-11-20)
- ✅ Basic monitoring functionality
- ✅ AI video summarization
- ✅ Email notifications
- ✅ GitHub Actions automation

## 🤝 Contributing

Issues and Pull Requests are welcome!

If you have questions or suggestions, please submit them on the [Issues](../../issues) page.

## 📄 License

MIT License - Free to use and modify

---

**🎉 Start monitoring your favorite YouTube channels now!**

