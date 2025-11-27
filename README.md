# YouTube 视频监控系统

**中文** | [English](./README_EN.md)

自动监控YouTube频道更新，使用AI生成中文视频总结并通过邮件通知订阅者。

## ✨ 核心功能

- 🔍 **自动监控**: 每小时自动检测YouTube频道新视频
- 🌐 **智能字幕**: 自动获取视频原始语言字幕（英语/日语/韩语等）
- 🤖 **AI总结**: 使用Gemini AI生成结构化中文内容大纲
- 📧 **邮件推送**: 发送美观的HTML格式邮件通知
- ⏰ **全天运行**: GitHub Actions 24小时自动运行
- 💰 **完全免费**: 所有服务使用免费API配额

## 🚀 5分钟快速部署

### 第一步：获取API密钥（5分钟）

| 服务 | 获取地址 | 说明 | 免费配额 |
|------|---------|------|----------|
| **YouTube API** | [Google Cloud Console](https://console.cloud.google.com/) | 启用 YouTube Data API v3 → 创建API密钥 | 10,000单位/天 |
| **Gemini AI** | [Google AI Studio](https://makersuite.google.com/app/apikey) | 点击"创建API密钥" | 15请求/分钟 |
| **Resend** | [resend.com](https://resend.com/api-keys) | 注册账户 → 创建API密钥 | 100封/天 |
| **Azure Speech** | [Azure Portal](https://portal.azure.com/) | 创建"语音服务"资源 | 5小时/月 ⚠️ |

⚠️ **Azure Speech（可选）**: 仅在视频禁用字幕时使用，会下载音频转文本。大部分视频有字幕，可以先不配置。

### 第二步：部署到GitHub（2分钟）

1. **Fork本仓库** - 点击右上角Fork按钮 

2. **配置Secrets** - 进入你的仓库 `Settings` → `Secrets and variables` → `Actions`，添加以下密钥：
   
   **API密钥（必需）：**
   - `YOUTUBE_API_KEY` - 你的YouTube API密钥
   - `GEMINI_API_KEY` - 你的Gemini API密钥
   - `RESEND_API_KEY` - 你的Resend API密钥
   
   **邮件配置（必需）：**
   - `EMAIL_FROM` - 发件人地址，格式：`YouTube Monitor <onboarding@resend.dev>`
   - `EMAIL_SUBSCRIBERS` - 订阅者邮箱，多个邮箱用逗号分隔，如：`user1@gmail.com,user2@outlook.com`
   
   **Azure语音服务（可选，仅在视频无字幕时使用）：**
   - `AZURE_SPEECH_KEY` - Azure语音服务密钥
   - `AZURE_SPEECH_REGION` - Azure服务区域（如：`eastus`）

3. **修改配置** - 编辑 `config.json` 文件（仅配置要监控的频道）：

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

**获取YouTube频道ID的方法：**
- 访问YouTube频道页面，URL中的 `UC_x5XG1OV2P6uZZ5FSM9Ttw` 就是频道ID
- 或右键查看页面源代码，搜索 `"channelId"`

**邮件配置说明：**
- ⚠️ **重要**：邮件配置（发件人和订阅者）已移至 GitHub Secrets
- 📖 详细配置方法请查看：[GitHub Secrets 配置指南](./SECRETS_GUIDE.md)
- 不要在 `config.json` 中配置邮箱信息

4. **启用Actions** - 进入 `Actions` 标签页 → 启用工作流 → 完成！

系统将每小时自动检查YouTube更新并发送邮件通知。

## 📋 配置详解

### config.json 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `channels` | Array | ✅ | 要监控的YouTube频道列表 |
| `channels[].id` | String | ✅ | YouTube频道ID（以UC开头） |
| `channels[].name` | String | ✅ | 频道显示名称（用于邮件标题） |
| `check_hours` | Number | ❌ | 检查最近多少小时的视频（默认24） |

**注意**: `subscribers` 和 `email.from` 已移至 GitHub Secrets 配置

### GitHub Secrets 详细配置

#### 必需的 Secrets（7个）

| Secret名称 | 说明 | 示例 | 获取方法 |
|-----------|------|------|---------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 密钥 | `AIzaSyC...` | [Google Cloud Console](https://console.cloud.google.com/) |
| `GEMINI_API_KEY` | Google Gemini AI 密钥 | `AIzaSyD...` | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `RESEND_API_KEY` | Resend 邮件服务密钥 | `re_...` | [Resend Dashboard](https://resend.com/api-keys) |
| `EMAIL_FROM` | 发件人地址 | `YouTube Monitor <onboarding@resend.dev>` | Resend验证域名或使用测试域名 |
| `EMAIL_SUBSCRIBERS` | 订阅者邮箱（逗号分隔） | `user1@gmail.com,user2@gmail.com` | 你的邮箱地址 |
| `AZURE_SPEECH_KEY` | Azure 语音服务密钥（可选） | `abc123...` | [Azure Portal](https://portal.azure.com/) |
| `AZURE_SPEECH_REGION` | Azure 服务区域（可选） | `eastus` | Azure 语音服务的位置/区域 |

#### 配置步骤

1. 进入你 Fork 的仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 输入上表中的 Secret 名称和对应的值
5. 点击 `Add secret`
6. 重复步骤3-5，添加所有 7 个 Secrets

#### 服务免费额度说明

| 服务 | 免费额度 | 足够用于 |
|------|---------|---------|
| YouTube Data API | 10,000单位/天 | 监控 100+ 个频道 |
| Gemini AI | 15请求/分钟 | 每小时处理多个视频 |
| Resend | 100封/天 或 3,000封/月 | 个人使用绰绰有余 |
| Azure Speech | 5小时/月 | 处理约 30 个无字幕视频 |
| GitHub Actions | 2,000分钟/月（公共仓库无限） | 全天候运行 |

### 支持多频道配置

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

## 🔧 本地测试

### 安装依赖

```bash
pip install -r requirements.txt
```

### 设置环境变量

**Windows PowerShell:**
```powershell
$env:YOUTUBE_API_KEY="你的API密钥"
$env:GEMINI_API_KEY="你的API密钥"
$env:RESEND_API_KEY="你的API密钥"
$env:EMAIL_FROM="YouTube Monitor <onboarding@resend.dev>"
$env:EMAIL_SUBSCRIBERS="your-email@example.com"

# 可选：Azure语音服务（仅在视频无字幕时使用）
$env:AZURE_SPEECH_KEY="你的Azure密钥"
$env:AZURE_SPEECH_REGION="eastus"

# 可选：启用免费代理（默认启用，避免IP被封）
$env:USE_PROXY="true"  # 设置为 "false" 禁用代理
```

**Linux/Mac:**
```bash
export YOUTUBE_API_KEY="你的API密钥"
export GEMINI_API_KEY="你的API密钥"
export RESEND_API_KEY="你的API密钥"
export EMAIL_FROM="YouTube Monitor <onboarding@resend.dev>"
export EMAIL_SUBSCRIBERS="your-email@example.com"

# 可选：Azure语音服务
export AZURE_SPEECH_KEY="你的Azure密钥"
export AZURE_SPEECH_REGION="eastus"
```

**多个订阅者：**
```powershell
$env:EMAIL_SUBSCRIBERS="user1@gmail.com,user2@outlook.com"
```


### 运行程序

```bash
python monitor.py
```

**注意：** 程序运行一次后自动退出。定时执行由GitHub Actions负责。

## ⚙️ 自定义运行频率

编辑 `.github/workflows/monitor.yml` 修改cron表达式：

```yaml
schedule:
  - cron: '0 * * * *'      # 每小时
  # - cron: '0 */2 * * *'  # 每2小时
  # - cron: '0 */6 * * *'  # 每6小时  
  # - cron: '0 9,21 * * *' # 每天9点和21点
```

## 💡 工作流程

```
GitHub Actions (每小时触发)
    ↓
检查YouTube频道新视频
    ↓
尝试获取视频字幕（优先原始语言）
    ↓
字幕可用？ ─── 否 ──→ 使用第三方API下载音频 → Azure Speech转文本
    ↓ 是
    ↓
Gemini AI生成中文总结
    ↓
发送HTML格式邮件
    ↓
保存状态到Git仓库
    ↓
程序退出，等待下次触发
```

**特色功能：**
- 🌐 **智能语言检测**: 自动识别视频原始语言，优先获取手动字幕
- 🔊 **音频转录备份**: 当字幕不可用时，自动使用第三方API下载音频并转文本（无需配置cookies）
- 🎨 **美观邮件**: HTML格式，响应式设计，移动端友好
- 💾 **状态持久化**: 记录到Git仓库，避免重复通知
- 🔄 **自动去重**: 已处理的视频不会重复发送
- 🛡️ **绕过IP限制**: 使用第三方API下载音频，无需担心GitHub Actions IP被封禁
- 🔌 **智能代理**: 自动获取免费代理，避免IP被封（支持多个代理源，自动测试可用性）

## 📈 资源消耗估算

| 监控频道数 | 运行频率 | 月度耗时 | Actions配额 |
|-----------|---------|---------|------------|
| 10个 | 每小时 | ~360分钟 | 18% |
| 30个 | 每小时 | ~540分钟 | 27% |
| 50个 | 每2小时 | ~360分钟 | 18% |

所有场景都远低于2,000分钟免费配额！

## ⚠️ 重要提示

### 功能说明
- ✅ **首次运行**: 检查最近24小时视频，之后仅检测新视频
- ✅ **字幕优先**: 自动获取原始语言字幕（英/日/韩/西/中等）
- 🔊 **音频备份**: 视频禁用字幕时，自动下载音频转文本（需配置Azure Speech）
- 🛡️ **IP限制绕过**: 使用第三方API下载音频，无需担心GitHub Actions IP被封禁

### 成本控制
- ⚠️ **Azure可选**: 大部分YouTube视频都有字幕，Azure Speech仅作为备选方案
- 💰 **免费额度**: Azure 免费额度每月5小时，如果监控的频道都有字幕，可以不配置
- ✅ **邮件配额**: Resend免费版每天100封，足够个人使用

### 配置建议
- ⚠️ **测试邮箱限制**: 使用`onboarding@resend.dev`只能发给已验证的邮箱
- 💡 **推荐方案**: 在 Resend 配置并验证自己的域名，获得更高额度
- ⚠️ **API限制**: YouTube API每天10,000单位，监控100个频道无压力

### 隐私保护
- 🔒 **敏感信息**: 所有 API 密钥和邮箱配置都在 GitHub Secrets 中
- ✅ **安全存储**: Secrets 加密存储，不会暴露在代码或日志中
- 👥 **多用户友好**: 每个人 Fork 后设置自己的 Secrets，互不影响

### 音频转录流程（当字幕不可用时）
1. 使用第三方 API (ytb2mp3.xyz) 下载 MP3 音频
2. 使用 FFmpeg 转换 MP3 → WAV 格式
3. Azure Speech SDK 进行语音识别（支持中英日韩多语言）
4. 返回文本内容用于 AI 总结

**优势**: 完全绕过 YouTube IP 检测，无需配置 cookies

## 🐛 常见问题

<details>
<summary><b>Q: GitHub Actions没有自动运行？</b></summary>

A: 
1. 检查是否在 Actions 页面启用了工作流
2. 确认所有 GitHub Secrets 已正确配置
3. 查看 Actions 页面的运行日志排查错误
4. 首次 Fork 后需要手动触发一次或等待定时任务启动
</details>

<details>
<summary><b>Q: GitHub Actions 提示权限错误 (403)?</b></summary>

A:
这是因为工作流没有写入权限，无法提交 `last_videos.json` 状态文件。

**解决方法：**
1. 进入仓库 `Settings` → `Actions` → `General`
2. 找到 "Workflow permissions"
3. 选择 **"Read and write permissions"**
4. 勾选 **"Allow GitHub Actions to create and approve pull requests"**（可选）
5. 点击保存
6. 重新运行工作流

**注意**: 此权限仅用于更新 `last_videos.json` 文件，确保不重复发送通知。
</details>

<details>
<summary><b>Q: FFmpeg 安装失败？</b></summary>

A:
如果看到 FFmpeg 相关错误，确认 `.github/workflows/monitor.yml` 包含：

```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y ffmpeg
```

最新版本已包含此步骤，拉取最新代码即可。
</details>

<details>
<summary><b>Q: 收不到邮件？</b></summary>

A:
1. **检查 API 密钥**: 确认 `RESEND_API_KEY` 配置正确
2. **验证邮箱**: 使用 `onboarding@resend.dev` 时，需在 Resend 后台添加并验证收件人邮箱
3. **检查垃圾箱**: 邮件可能被标记为垃圾邮件
4. **域名验证**: 建议在 Resend 配置并验证自己的域名
5. **配额限制**: 免费版每天限 100 封邮件

**推荐方案**: 
- 配置自己的域名并验证
- 使用 Gmail/Outlook 等可靠邮箱接收
</details>

<details>
<summary><b>Q: 无法获取字幕？</b></summary>

A:
1. 确认视频有可用字幕（手动或自动生成）
2. 某些视频禁用了字幕下载功能
3. 如果配置了 Azure Speech，系统会自动下载音频转录
4. 系统会在邮件中说明字幕获取状态
</details>

<details>
<summary><b>Q: Azure Speech 转录失败？</b></summary>

A:
1. 确认 `AZURE_SPEECH_KEY` 和 `AZURE_SPEECH_REGION` 配置正确
2. 检查 Azure 服务区域格式（小写，如 `eastus`、`westus2`）
3. 确认 Azure 免费配额未用完（5小时/月）
4. 查看 Actions 日志中的详细错误信息

**注意**: Azure Speech 仅在字幕不可用时才会使用，大部分视频有字幕，可不配置。
</details>

<details>
<summary><b>Q: YouTube 下载被阻止？</b></summary>

A:
系统已使用第三方 API (ytb2mp3.xyz) 绕过 YouTube IP 限制：
- ✅ 无需配置 cookies
- ✅ 适用于 GitHub Actions
- ✅ 自动处理音频下载

如果第三方 API 不可用，系统会跳过该视频并在邮件中说明。
</details>

<details>
<summary><b>Q: 想监控更多频道？</b></summary>

A:
- 理论上无限制
- 建议不超过 100 个（API 配额考虑）
- 可调整 `check_hours` 参数减少 API 调用
- YouTube API 每天 10,000 单位配额足够监控大量频道
</details>

<details>
<summary><b>Q: 如何保护隐私？邮箱不想暴露在公开仓库？</b></summary>

A:
✅ 已解决！所有敏感信息都存储在 GitHub Secrets 中：
- 邮箱配置不在 `config.json` 中
- 所有 API 密钥加密存储
- Fork 后设置自己的 Secrets，互不影响
- 公开仓库中看不到任何隐私信息

**配置位置**: `Settings` → `Secrets and variables` → `Actions`
</details>

<details>
<summary><b>Q: 如何手动触发测试？</b></summary>

A:
1. 进入仓库的 `Actions` 标签
2. 选择 `YouTube Monitor` 工作流
3. 点击 `Run workflow` 按钮
4. 选择分支（通常是 main）
5. 点击绿色的 `Run workflow` 确认
6. 等待几分钟查看运行结果
</details>

<details>
<summary><b>Q: 代理功能如何工作？</b></summary>

A:
系统默认启用免费代理功能，自动从多个源获取可用代理：
- ✅ **自动获取**: 从 proxy-list.download、free-proxy-list.net 等网站获取
- ✅ **自动测试**: 测试代理可用性，只使用可用代理
- ✅ **智能切换**: 请求失败时自动切换代理重试
- ✅ **可禁用**: 设置环境变量 `USE_PROXY=false` 禁用代理

**代理源：**
1. proxy-list.download - HTTP 代理
2. free-proxy-list.net - 免费代理列表
3. geonode.com - 地理节点代理

**注意**: 免费代理可能不稳定，系统会自动测试并选择可用的代理。
</details>

<details>
<summary><b>Q: 如何禁用代理？</b></summary>

A:
如果不需要代理功能，可以在环境变量中设置：

**本地测试：**
```powershell
$env:USE_PROXY="false"
```

**GitHub Actions：**
在 `.github/workflows/monitor.yml` 中添加环境变量：
```yaml
env:
  USE_PROXY: "false"
```

禁用后，所有请求将直连，不使用代理。
</details>

## 📝 项目文件说明

```
gpt_information_summary/
├── monitor.py              # 主程序
├── config.json             # 用户配置文件
├── last_videos.json        # 状态记录（自动生成）
├── requirements.txt        # Python依赖
├── README.md              # 本文档
├── README_EN.md           # 英文文档
├── test_audio_download.py  # 音频下载测试脚本
├── test_full_pipeline.py   # 完整流程测试脚本
└── .github/workflows/
    └── monitor.yml        # GitHub Actions配置
```

## 🏗️ 技术架构

### 核心技术栈
- **语言**: Python 3.11+
- **YouTube API**: Google YouTube Data API v3
- **AI 模型**: Google Gemini 2.5 Flash
- **邮件服务**: Resend API
- **语音识别**: Azure Cognitive Services Speech SDK
- **字幕获取**: youtube-transcript-api
- **音频下载**: 第三方 API (ytb2mp3.xyz)
- **音频处理**: FFmpeg
- **CI/CD**: GitHub Actions

### 系统流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions 定时触发                    │
│                        (每小时运行)                           │
└────────────────────┬────────────────────────────────────────┘
                     ↓
        ┌────────────────────────────┐
        │   YouTube Data API v3      │
        │   获取频道最新视频列表        │
        └────────────┬───────────────┘
                     ↓
        ┌────────────────────────────┐
        │   检查 last_videos.json    │
        │   过滤已处理的视频           │
        └────────────┬───────────────┘
                     ↓
        ┌────────────────────────────┐
        │ 尝试获取视频字幕            │
        │ (youtube-transcript-api)   │
        └────────┬────────────┬──────┘
                 │            │
          字幕可用 │            │ 字幕不可用
                 ↓            ↓
        ┌────────────┐  ┌──────────────────┐
        │  提取文本   │  │ 第三方API下载音频 │
        └─────┬──────┘  │  (ytb2mp3.xyz)   │
              │         └────────┬─────────┘
              │                  ↓
              │         ┌──────────────────┐
              │         │ FFmpeg转换格式    │
              │         │  (MP3 → WAV)     │
              │         └────────┬─────────┘
              │                  ↓
              │         ┌──────────────────┐
              │         │ Azure Speech SDK │
              │         │   语音转文本      │
              │         └────────┬─────────┘
              │                  │
              └──────────┬───────┘
                         ↓
              ┌──────────────────────┐
              │   Gemini AI 生成总结  │
              │  (gemini-2.5-flash)  │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │  Resend API 发送邮件  │
              │   (HTML格式)          │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ 更新 last_videos.json │
              │  (Git commit & push)  │
              └──────────────────────┘
```

### 关键设计决策

1. **字幕优先策略**: 优先使用字幕，减少 Azure Speech 配额消耗
2. **第三方音频下载**: 绕过 YouTube IP 限制，无需 cookies 配置
3. **环境变量配置**: 敏感信息存储在 GitHub Secrets，保护隐私
4. **状态持久化**: 使用 Git 仓库存储状态，避免重复通知
5. **HTML 邮件**: 提升阅读体验，支持移动端

## 📅 更新日志

### v2.0 (2025-11-27)
- ✅ 添加音频转录功能（Azure Speech）
- ✅ 使用第三方 API 下载音频，绕过 IP 限制
- ✅ 支持多语言字幕自动检测
- ✅ 优化邮件 HTML 格式
- ✅ 隐私保护：敏感信息移至 GitHub Secrets

### v1.0 (2025-11-20)
- ✅ 基础监控功能
- ✅ AI 视频总结
- ✅ 邮件通知
- ✅ GitHub Actions 自动化

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

如有问题或建议，请在 [Issues](../../issues) 页面提出。

## 📄 开源协议

MIT License - 自由使用和修改

---

**🎉 立即开始监控你喜欢的 YouTube 频道吧！**

