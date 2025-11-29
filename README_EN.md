# YouTube Video Monitor & AI Summary System

[中文](./README.md) | **English**

Automatically monitor YouTube channel updates, transcribe videos in the background, generate AI summaries, and send email notifications.

## ✨ Features

- 🔍 **Auto Monitor**: Scheduled check for new YouTube videos (GitHub Actions)
- 🎙️ **Async Transcription**: Background server processes audio transcription (task queue)
- 🤖 **AI Summary**: Generate structured summaries using Google Gemini
- 📧 **Email Alerts**: Beautiful HTML formatted email notifications
- ⏰ **24/7 Running**: Fully automated workflow
- 💾 **Persistent Storage**: Task states saved, restart-safe
- 🚀 **Highly Scalable**: Queue-based processing for many videos

## 🏗️ Architecture

```
┌──────────────────────────────┐
│  Monitor (GitHub Actions)    │
│  - Check new videos          │
│  - Submit transcription jobs │
│  - Check completion status   │
│  - Generate AI summaries     │
│  - Send emails               │
└────────┬───────────┬─────────┘
         │           │
    Submit Job   Query Status
         │           │
         ▼           ▼
┌──────────────────────────────┐
│  Server (VPS continuous run) │
│  ┌────────────────────────┐  │
│  │  Task Queue (FIFO)     │  │
│  │  T1 → T2 → T3 → ...   │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │  Worker Thread         │  │
│  │  1. Download audio     │  │
│  │  2. Whisper transcribe │  │
│  │  3. Save results       │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- VPS Server (for transcription service, recommended: 2 cores, 4GB RAM)
- GitHub Account

### Step 1: Deploy Transcription Server

```bash
# SSH to your server
ssh user@your-server.com

# Clone repository
git clone https://github.com/your-username/gpt_information_summary.git
cd gpt_information_summary/audio_download_server

# Install dependencies
pip install -r requirements.txt

# Start service
python server_v2.py
```

For production, use systemd. See: [COMPLETE_DEPLOYMENT_GUIDE.md](COMPLETE_DEPLOYMENT_GUIDE.md)

### Step 2: Configure Monitor

#### 2.1 Get API Keys

| Service | URL | Free Quota |
|---------|-----|------------|
| YouTube API | [Google Cloud](https://console.cloud.google.com/) | 10,000 units/day |
| Gemini AI | [AI Studio](https://makersuite.google.com/app/apikey) | 15 requests/min |
| Resend | [resend.com](https://resend.com/api-keys) | 100 emails/day |

#### 2.2 Configure GitHub Secrets

Fork this repo, then go to `Settings` → `Secrets and variables` → `Actions`, add:

- `YOUTUBE_API_KEY` - YouTube API key
- `GEMINI_API_KEY` - Gemini AI key
- `RESEND_API_KEY` - Resend key
- `EMAIL_FROM` - Sender email
- `EMAIL_SUBSCRIBERS` - Recipient emails (comma-separated)
- `AUDIO_SERVER_URL` - Server URL (e.g., `http://your-server.com:5000`)
- `AUDIO_SERVER_API_KEY` - Server API key

#### 2.3 Configure Channels

Edit `config.json`:

```json
{
  "channels": [
    {
      "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
      "name": "Google Developers"
    }
  ],
  "check_hours": 6
}
```

#### 2.4 Enable GitHub Actions

1. Go to `Actions` tab
2. Enable workflows
3. `Settings` → `Actions` → `General` → "Read and write permissions"

Done! The system will run every 6 hours automatically.

## 📋 Key Features

### Async Processing
- ✅ Monitor doesn't wait for transcription (avoid timeout)
- ✅ Server processes in background (10-30 min/video)
- ✅ Results fetched on next run

### Task Queue
- ✅ FIFO queue, sequential processing
- ✅ Single-threaded, resource-efficient
- ✅ Support task retry

### Storage Optimization
- ✅ Transcription texts stored separately
- ✅ jobs.json stays lightweight (always < 100KB)
- ✅ Supports unlimited videos

## 📊 Performance

| Metric | Value |
|--------|-------|
| Task submission | < 1s |
| Video transcription | 10-30 min |
| Queue capacity | 48-144 videos/day |
| Memory usage | ~500MB (Server) |

## 🐛 Troubleshooting

See documentation:
- [Server Deadlock Fix](audio_download_server/DEADLOCK_FIX.md)
- [Storage Optimization](audio_download_server/STORAGE_OPTIMIZATION.md)
- [Duplicate Jobs Fix](audio_download_server/DUPLICATE_FIX.md)

## 📚 Documentation

- [Complete Deployment Guide](COMPLETE_DEPLOYMENT_GUIDE.md)
- [System Architecture](SYSTEM_ARCHITECTURE.md)
- [Server V2 Manual](audio_download_server/README_V2.md)

## 📄 License

MIT License

---

**Enjoy your automated video summary service!** 🎉

