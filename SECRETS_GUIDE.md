# 配置密钥指南

本项目需要在GitHub仓库的Settings -> Secrets and variables -> Actions中配置以下密钥：

## 必需的密钥

### 1. YOUTUBE_API_KEY
YouTube Data API v3 密钥

**获取方式：**
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 "YouTube Data API v3"
4. 在"凭据"中创建API密钥
5. 复制API密钥

### 2. GEMINI_API_KEY
Google Gemini AI API 密钥

**获取方式：**
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建API密钥
3. 复制密钥

### 3. RESEND_API_KEY
Resend邮件服务API密钥

**获取方式：**
1. 访问 [Resend](https://resend.com/)
2. 注册账号（免费额度：每月3000封邮件）
3. 在Dashboard中创建API密钥
4. 复制密钥

### 4. AZURE_SPEECH_KEY
Azure 语音服务密钥

**获取方式：**
1. 访问 [Azure Portal](https://portal.azure.com/)
2. 创建"语音服务"资源（免费层：每月5小时音频转录）
3. 在"密钥和终结点"中复制密钥1或密钥2

### 5. AZURE_SPEECH_REGION
Azure 语音服务区域

**获取方式：**
- 在Azure语音服务的"密钥和终结点"页面查看"位置/区域"
- 例如：`eastus`、`westus2`、`eastasia`等

### 6. EMAIL_FROM
发送邮件的邮箱地址

**格式：**
```
Your Name <noreply@yourdomain.com>
```

**注意：**
- 需要在Resend中验证此域名或使用Resend提供的测试域名
- 免费用户可以使用 `onboarding@resend.dev`

### 7. EMAIL_SUBSCRIBERS
接收邮件的订阅者邮箱（多个邮箱用逗号分隔）

**格式：**
```
user1@example.com,user2@example.com
```

或单个邮箱：
```
user@example.com
```

## 配置步骤

1. 进入GitHub仓库
2. 点击 `Settings` -> `Secrets and variables` -> `Actions`
3. 点击 `New repository secret`
4. 输入密钥名称和值
5. 点击 `Add secret`
6. 重复以上步骤添加所有7个密钥

## 成本说明

所有服务都提供免费额度，足够个人使用：

- **YouTube Data API**: 每天免费10,000配额单位（查询视频信息消耗很少）
- **Gemini API**: 免费额度每分钟15次请求
- **Resend**: 每月免费3,000封邮件
- **Azure Speech**: 每月免费5小时音频转录
- **GitHub Actions**: 公共仓库免费无限使用

## 验证配置

配置完成后，可以手动触发工作流测试：
1. 进入仓库的 `Actions` 标签
2. 选择 `YouTube Monitor` 工作流
3. 点击 `Run workflow` -> `Run workflow`
4. 查看运行日志，确认是否配置正确

