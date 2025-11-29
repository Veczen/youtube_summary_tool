# YouTube 视频监控与AI总结系统

**中文** | [English](./README_EN.md)

自动监控YouTube频道更新，后台转录视频内容，使用AI生成中文总结并通过邮件通知订阅者。

## ✨ 核心功能

- 🔍 **自动监控**: 定时检测YouTube频道新视频（GitHub Actions）
- 🎙️ **异步转录**: 后台服务器处理音频转录（支持任务队列）
- 🤖 **AI总结**: 使用Google Gemini生成结构化中文内容总结
- 📧 **邮件推送**: 发送美观的HTML格式邮件通知
- ⏰ **全天运行**: 24/7自动化工作流
- 💾 **持久化存储**: 任务状态保存，重启不丢失
- 🚀 **高可扩展**: 支持排队处理大量视频

## 🏗️ 系统架构

```
┌─────────────────────────────────────┐
│  Monitor (GitHub Actions 定时执行)    │
│  - 检查新视频                         │
│  - 提交转录任务                       │
│  - 检查完成状态                       │
│  - 生成AI总结                        │
│  - 发送邮件                          │
└────────┬──────────────┬─────────────┘
         │              │
    提交任务        查询状态
         │              │
         ▼              ▼
┌─────────────────────────────────────┐
│  Server (VPS 持续运行)                │
│  ┌────────────────────────────────┐ │
│  │  任务队列 (FIFO)                 │ │
│  │  Task1 → Task2 → Task3 → ...   │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Worker Thread                 │ │
│  │  1. 下载音频 (10-30分钟)         │ │
│  │  2. Whisper转录                 │ │
│  │  3. 保存结果                    │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 工作流程

**第一次运行（发现新视频）：**
```
Monitor → 发现新视频 → 提交转录任务 → Server加入队列 → Monitor继续
```

**Server后台处理：**
```
Server → 取任务 → 下载音频 → Whisper转录 → 保存文本
```

**第二次运行（获取总结）：**
```
Monitor → 检查待处理 → 获取转录 → AI总结 → 发邮件
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- VPS服务器（用于运行转录服务，推荐：2核4G）
- GitHub账号

### 第一步：部署转录服务器

#### 1.1 准备服务器

```bash
# SSH连接
ssh user@your-server.com

# 克隆代码
git clone https://github.com/your-username/gpt_information_summary.git
cd gpt_information_summary/audio_download_server

# 安装依赖
pip install -r requirements.txt
```

#### 1.2 启动服务

**测试启动：**
```bash
python server_v2.py
```

**生产环境（systemd）：**

创建 `/etc/systemd/system/youtube-transcribe.service`：

```ini
[Unit]
Description=YouTube Transcription Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/audio_download_server
Environment="AUDIO_SERVER_API_KEY=your-secret-key"
ExecStart=/usr/bin/python3 /path/to/server_v2.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start youtube-transcribe
sudo systemctl enable youtube-transcribe
```

#### 1.3 验证

```bash
curl -H "X-API-Key: your-secret-key" http://localhost:5000/health
```

**详细部署:** [COMPLETE_DEPLOYMENT_GUIDE.md](COMPLETE_DEPLOYMENT_GUIDE.md)

---

### 第二步：配置Monitor

#### 2.1 获取API密钥

| 服务 | 获取地址 | 免费配额 |
|------|---------|---------|
| YouTube API | [Google Cloud](https://console.cloud.google.com/) | 10,000单位/天 |
| Gemini AI | [AI Studio](https://makersuite.google.com/app/apikey) | 15请求/分钟 |
| Resend | [resend.com](https://resend.com/api-keys) | 100封/天 |

#### 2.2 配置GitHub Secrets

Fork本仓库后，进入 `Settings` → `Secrets and variables` → `Actions`，添加：

| Secret名称 | 说明 | 示例 |
|-----------|------|------|
| `YOUTUBE_API_KEY` | YouTube API密钥 | `AIzaSyC...` |
| `GEMINI_API_KEY` | Gemini AI密钥 | `AIzaSyD...` |
| `RESEND_API_KEY` | Resend密钥 | `re_...` |
| `EMAIL_FROM` | 发件人 | `Monitor <noreply@yourdomain.com>` |
| `EMAIL_SUBSCRIBERS` | 收件人 | `user1@gmail.com,user2@gmail.com` |
| `AUDIO_SERVER_URL` | Server地址 | `http://your-server.com:5000` |
| `AUDIO_SERVER_API_KEY` | Server密钥 | `your-secret-key` |

#### 2.3 配置频道

编辑 `config.json`：

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

#### 2.4 启用Actions

1. 进入 `Actions` 标签
2. 启用workflows
3. `Settings` → `Actions` → `General` → "Read and write permissions"

完成！系统将每6小时自动运行。

---

## 📋 系统特性

### 异步处理
- ✅ Monitor不等待转录完成（避免GitHub Actions超时）
- ✅ Server后台处理（10-30分钟/视频）
- ✅ 下次运行时获取结果

### 任务队列
- ✅ FIFO队列，按顺序处理
- ✅ 单线程处理，避免资源过载
- ✅ 支持任务重试

### 存储优化
- ✅ 转录文本单独存储（`transcripts/`目录）
- ✅ jobs.json保持轻量（永远几十KB）
- ✅ 支持无限数量视频

### 错误处理
- ✅ 网络超时自动重试
- ✅ 失败任务可重新排队
- ✅ 详细日志

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 任务提交 | < 1秒 |
| 单视频转录 | 10-30分钟 |
| 队列能力 | 48-144视频/天 |
| jobs.json | < 100KB |
| Server内存 | ~500MB |

---

## 🔧 本地测试

### Monitor测试

```bash
# 设置环境变量
export YOUTUBE_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export RESEND_API_KEY="your-key"
export EMAIL_FROM="Monitor <your@email.com>"
export EMAIL_SUBSCRIBERS="subscriber@email.com"
export AUDIO_SERVER_URL="http://localhost:5000"
export AUDIO_SERVER_API_KEY="your-key"

# 运行
python monitor.py
```

### Server测试

```bash
cd audio_download_server
python server_v2.py

# 另一终端测试
python quick_test.py
```

---

## ⚙️ 运行频率配置

编辑 `.github/workflows/monitor.yml`：

```yaml
schedule:
  - cron: '0 */6 * * *'     # 每6小时（推荐）
  # - cron: '0 */3 * * *'   # 每3小时
  # - cron: '0 */12 * * *'  # 每12小时
```

---

## ⚠️ 注意事项

### Server端
- 📌 使用VPS或云服务器
- 📌 需要稳定网络
- 📌 定期备份 `jobs.json` 和 `transcripts/`
- 📌 监控磁盘空间

### Monitor端
- 📌 首次运行检查最近6-24小时
- 📌 `pending_jobs.json` 记录待处理任务
- 📌 需要GitHub Actions Write权限
- 📌 所有敏感信息在Secrets中

### API配额
- YouTube: 10,000单位/天
- Gemini: 15请求/分钟
- Resend: 100封/天

---

## 🐛 常见问题

<details>
<summary><b>Q: Server收到请求后卡住？</b></summary>

A: 已修复死锁问题。请使用最新的 `server_v2.py`。参考：[DEADLOCK_FIX.md](audio_download_server/DEADLOCK_FIX.md)
</details>

<details>
<summary><b>Q: jobs.json变得很大？</b></summary>

A: 已优化！转录文本单独存储，jobs.json永远保持轻量。参考：[STORAGE_OPTIMIZATION.md](audio_download_server/STORAGE_OPTIMIZATION.md)
</details>

<details>
<summary><b>Q: 同一视频有重复任务？</b></summary>

A: 已修复！error状态任务会重新排队而不是创建新任务。参考：[DUPLICATE_FIX.md](audio_download_server/DUPLICATE_FIX.md)
</details>

<details>
<summary><b>Q: GitHub Actions无权限？</b></summary>

A: 
1. `Settings` → `Actions` → `General`
2. 选择 "Read and write permissions"
3. 保存并重新运行
</details>

<details>
<summary><b>Q: 收不到邮件？</b></summary>

A:
1. 检查 `RESEND_API_KEY` 配置
2. 验证域名或使用测试域名
3. 检查垃圾箱
4. 查看GitHub Actions日志
</details>

<details>
<summary><b>Q: 转录失败？</b></summary>

A:
1. 检查网络连接
2. 查看Server日志: `journalctl -u youtube-transcribe -f`
3. 验证第三方API是否可用
4. 检查Whisper模型是否正确加载
</details>

<details>
<summary><b>Q: 如何清理旧数据？</b></summary>

A:
```bash
# 清理30天前的转录文本
find transcripts -name "*.txt" -mtime +30 -delete

# 或运行清理脚本
cd audio_download_server
python clean_jobs.py
```
</details>

---

## 📁 项目结构

```
gpt_information_summary/
├── monitor.py                 # Monitor主程序
├── config.json                # 频道配置
├── last_videos.json           # 已处理视频
├── pending_jobs.json          # 待转录任务
├── requirements.txt           # Python依赖
│
├── audio_download_server/     # 转录服务器
│   ├── server_v2.py          # Server主程序
│   ├── temp_audio/           # 临时音频
│   │   └── jobs.json        # 任务元数据
│   ├── transcripts/          # 转录文本
│   │   ├── video1.txt
│   │   └── video2.txt
│   └── requirements.txt
│
└── .github/workflows/
    └── monitor.yml           # GitHub Actions配置
```

---

## 📚 文档

- [完整部署指南](COMPLETE_DEPLOYMENT_GUIDE.md) - 详细的部署步骤
- [系统架构说明](SYSTEM_ARCHITECTURE.md) - 深入了解系统设计
- [Server使用说明](audio_download_server/README_V2.md) - 转录服务器文档
- [存储优化说明](audio_download_server/STORAGE_OPTIMIZATION.md) - 存储优化详解
- [故障排查指南](audio_download_server/TROUBLESHOOTING.md) - 问题排查

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**享受自动化的视频内容总结服务！** 🎉

