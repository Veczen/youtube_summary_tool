# GitHub Secrets 配置指南

## 为什么使用 GitHub Secrets？

为了保护隐私和安全，邮箱地址等敏感信息不应该直接写在代码仓库中。使用 GitHub Secrets 可以：
- ✅ 保护个人隐私（邮箱不会暴露在公开仓库）
- ✅ 每个人可以使用自己的配置（Fork后设置自己的邮箱）
- ✅ 更安全（API密钥和邮箱配置都加密存储）

## 必需的 GitHub Secrets

进入你的仓库 `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

### 1. API 密钥（3个）

| Secret名称 | 说明 | 示例 |
|-----------|------|------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 密钥 | `AIzaSyC...` |
| `GEMINI_API_KEY` | Google Gemini AI 密钥 | `AIzaSyD...` |
| `RESEND_API_KEY` | Resend 邮件服务密钥 | `re_abc...` |

### 2. 邮件配置（2个）

| Secret名称 | 说明 | 示例 |
|-----------|------|------|
| `EMAIL_FROM` | 发件人地址 | `YouTube Monitor <onboarding@resend.dev>` |
| `EMAIL_SUBSCRIBERS` | 订阅者邮箱列表 | `user1@gmail.com,user2@outlook.com` |

## 详细设置步骤

### EMAIL_FROM（发件人配置）

**格式**: `名称 <邮箱地址>`

**示例**:
```
YouTube Monitor <onboarding@resend.dev>
```

**注意事项**:
- 测试阶段使用 `onboarding@resend.dev`（Resend提供的测试邮箱）
- 使用测试邮箱时，只能发送到你在Resend账户中验证的邮箱
- 生产环境建议配置自己的域名（免费验证）

**如何验证自己的域名**:
1. 登录 [Resend](https://resend.com/)
2. 进入 Domains → Add Domain
3. 按提示添加DNS记录
4. 验证通过后使用：`YouTube Bot <noreply@yourdomain.com>`

### EMAIL_SUBSCRIBERS（订阅者邮箱）

**格式**: 多个邮箱用英文逗号分隔，不要有空格（系统会自动处理空格）

**示例**:
```
user1@gmail.com,user2@outlook.com,team@company.com
```

**支持的格式**:
- ✅ `email1@domain.com,email2@domain.com`
- ✅ `email1@domain.com, email2@domain.com`（有空格也可以）
- ✅ 单个邮箱：`user@domain.com`

## 本地测试配置

如果要在本地测试，设置环境变量：

**Windows PowerShell:**
```powershell
$env:YOUTUBE_API_KEY="your_youtube_api_key"
$env:GEMINI_API_KEY="your_gemini_api_key"
$env:RESEND_API_KEY="your_resend_api_key"
$env:EMAIL_FROM="YouTube Monitor <onboarding@resend.dev>"
$env:EMAIL_SUBSCRIBERS="your-email@example.com"
```

**Linux/Mac:**
```bash
export YOUTUBE_API_KEY="your_youtube_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
export RESEND_API_KEY="your_resend_api_key"
export EMAIL_FROM="YouTube Monitor <onboarding@resend.dev>"
export EMAIL_SUBSCRIBERS="your-email@example.com"
```

## 配置优先级

系统按以下优先级读取配置：

1. **环境变量**（最高优先级）
   - `EMAIL_FROM` → 覆盖 config.json 中的 `email.from`
   - `EMAIL_SUBSCRIBERS` → 覆盖 config.json 中的 `subscribers`

2. **config.json** 文件（备用）
   - 如果没有设置环境变量，会从文件读取
   - 适合本地开发测试

## 常见问题

**Q: 为什么我的邮件发送失败？**

A: 检查以下几点：
1. `RESEND_API_KEY` 是否正确
2. `EMAIL_FROM` 格式是否正确
3. 使用 `onboarding@resend.dev` 时，确保收件人邮箱已在Resend验证
4. 检查是否超过Resend免费配额（100封/天）

**Q: 如何验证配置是否正确？**

A: 
1. 在 GitHub Actions 中手动触发一次工作流
2. 查看运行日志，检查是否有错误信息
3. 确认收件箱是否收到邮件

**Q: 多个人Fork后如何各自配置？**

A: 
1. 每个人Fork后，在自己的仓库设置自己的Secrets
2. 修改 `config.json` 中的 `channels` 配置（监控的频道）
3. 不需要修改代码，只需要配置Secrets即可

**Q: 可以添加多少个订阅者？**

A: 理论上没有限制，但要注意：
- Resend免费版每天100封邮件
- 如果监控10个频道，每天有5个新视频，每封邮件发给10个订阅者 = 50封
- 合理规划订阅者数量和监控频道数量

## 安全建议

- ✅ 永远不要将API密钥和邮箱配置提交到Git仓库
- ✅ 使用GitHub Secrets管理所有敏感信息
- ✅ 定期轮换API密钥
- ✅ 不要在公开的Issue或PR中泄露配置信息

