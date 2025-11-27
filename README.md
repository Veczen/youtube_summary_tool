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

### GitHub Secrets 配置

| Secret名称 | 说明 | 示例 |
|-----------|------|------|
| `EMAIL_FROM` | 发件人地址 | `YouTube Monitor <onboarding@resend.dev>` |
| `EMAIL_SUBSCRIBERS` | 订阅者邮箱（逗号分隔） | `user1@gmail.com,user2@outlook.com` |

详细配置方法：📖 [GitHub Secrets 配置指南](./SECRETS_GUIDE.md)

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
字幕可用？ ─── 否 ──→ 下载音频 → Azure Speech转文本
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
- 🔊 **音频转录备份**: 当字幕不可用时，自动下载音频并使用Azure Speech转文本
- 🎨 **美观邮件**: HTML格式，响应式设计，移动端友好
- 💾 **状态持久化**: 记录到Git仓库，避免重复通知
- 🔄 **自动去重**: 已处理的视频不会重复发送

## 📈 资源消耗估算

| 监控频道数 | 运行频率 | 月度耗时 | Actions配额 |
|-----------|---------|---------|------------|
| 10个 | 每小时 | ~360分钟 | 18% |
| 30个 | 每小时 | ~540分钟 | 27% |
| 50个 | 每2小时 | ~360分钟 | 18% |

所有场景都远低于2,000分钟免费配额！

## ⚠️ 重要提示

- ✅ **首次运行**: 检查最近24小时视频，之后仅检测新视频
- ✅ **字幕优先**: 自动获取原始语言字幕（英/日/韩/西/中等）
- 🔊 **音频备份**: 视频禁用字幕时，自动下载音频转文本（需配置Azure Speech）
- ⚠️ **Azure可选**: 大部分YouTube视频都有字幕，Azure Speech仅作为备选方案
- 💰 **成本控制**: Azure免费额度每月5小时，如果监控的频道都有字幕，可以不配置
- ✅ **邮件配额**: Resend免费版每天100封，足够个人使用
- ⚠️ **测试邮箱**: 使用`onboarding@resend.dev`只能发给验证的邮箱
- ⚠️ **API限制**: YouTube API每天10,000单位，监控100个频道无压力

## 🐛 常见问题

<details>
<summary><b>Q: GitHub Actions没有自动运行？</b></summary>

A: 
1. 检查是否在 Actions 页面启用了工作流
2. 确认所有 GitHub Secrets 已正确配置
3. 查看 Actions 页面的运行日志排查错误
</details>

<details>
<summary><b>Q: GitHub Actions 提示权限错误 (403)?</b></summary>

A:
这是因为工作流没有写入权限。已在最新版本中修复，如果仍有问题：

1. 进入仓库 `Settings` → `Actions` → `General`
2. 找到 "Workflow permissions"
3. 选择 "Read and write permissions"
4. 保存设置
5. 重新运行工作流
</details>

<details>
<summary><b>Q: 收不到邮件？</b></summary>

A:
1. 检查 RESEND_API_KEY 是否正确
2. 使用测试邮箱时，确保收件人在Resend账户中已验证
3. 查看垃圾邮件文件夹
4. 建议配置并验证自己的域名
</details>

<details>
<summary><b>Q: 无法获取字幕？</b></summary>

A:
1. 确认视频有可用字幕（手动或自动生成）
2. 某些视频可能禁用字幕下载
3. 系统会自动跳过并在邮件中说明
</details>

<details>
<summary><b>Q: 想监控更多频道？</b></summary>

A:
- 理论上无限制
- 建议不超过100个（API配额考虑）
- 可调整 `check_hours` 参数减少API调用
</details>

## 📝 项目文件说明

```
gpt_information_summary/
├── monitor.py              # 主程序
├── test_config.py          # 配置验证脚本
├── config.json             # 用户配置文件
├── config.example.json     # 配置示例
├── last_videos.json        # 状态记录（自动生成）
├── requirements.txt        # Python依赖
├── README.md              # 本文档
└── .github/workflows/
    └── monitor.yml        # GitHub Actions配置
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

如有问题或建议，请在 [Issues](../../issues) 页面提出。

## 📄 开源协议

MIT License - 自由使用和修改

---
