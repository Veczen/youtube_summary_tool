import json
import os
import requests
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
import google.generativeai as genai
import resend

class YouTubeMonitor:
    def __init__(self):
        self.config = self.load_json('config.json')
        self.last_videos = self.load_json('last_videos.json')

        # 从环境变量覆盖邮件配置（如果存在）
        email_from = os.getenv('EMAIL_FROM')
        if email_from:
            if 'email' not in self.config:
                self.config['email'] = {}
            self.config['email']['from'] = email_from

        # 从环境变量获取订阅者邮箱（如果存在）
        subscribers = os.getenv('EMAIL_SUBSCRIBERS')
        if subscribers:
            # 支持多个邮箱，用逗号分隔
            self.config['subscribers'] = [email.strip() for email in subscribers.split(',')]


        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        resend.api_key = os.getenv('RESEND_API_KEY')
        self.audio_server_url = os.getenv('AUDIO_SERVER_URL')
        self.audio_server_api_key = os.getenv('AUDIO_SERVER_API_KEY', '')

    def load_json(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_json(self, filename, data):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_channel_uploads(self, channel_id):
        try:
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()

            uploads_playlist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.config.get('check_hours', 24))

            playlist_response = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist,
                maxResults=5
            ).execute()

            playlist_items = playlist_response.get('items', [])
            video_ids = [item['contentDetails']['videoId'] for item in playlist_items]
            privacy_map = self.get_video_privacy_status(video_ids)

            new_videos = self.filter_public_videos(
                playlist_items,
                privacy_map,
                cutoff_time,
                channel_id
            )

            return new_videos
        except Exception as e:
            print(f"获取频道 {channel_id} 视频失败: {e}")
            return []

    def request_transcript_from_server(self, video_id):
        """请求音频服务器返回转录文本"""
        if not self.audio_server_url:
            print("  - 未配置 AUDIO_SERVER_URL，无法获取转录")
            return None

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        endpoint = self.audio_server_url.rstrip('/') + '/transcribe'
        headers = {
            'Content-Type': 'application/json'
        }
        if self.audio_server_api_key:
            headers['X-API-Key'] = self.audio_server_api_key

        payload = {
            'url': video_url
        }

        try:
            print("  - 请求音频服务器进行转录...")
            response = requests.post(endpoint, json=payload, headers=headers, timeout=2000)
            if response.status_code != 200:
                print(f"  - 音频服务器返回错误: {response.status_code}")
                try:
                    error_payload = response.json()
                    print(f"  - 错误信息: {error_payload.get('error', 'unknown error')}")
                except ValueError:
                    print(f"  - 响应内容: {response.text[:200]}")
                return None

            data = response.json()
            if not data.get('success'):
                print(f"  - 音频服务器未能完成转录: {data.get('error', 'unknown error')}")
                return None

            transcript_text = data.get('text', '').strip()
            if not transcript_text:
                print("  - 音频服务器返回的文本为空")
                return None

            return {
                'text': transcript_text,
                'language': data.get('language', 'auto'),
                'language_code': data.get('language_code', 'auto'),
                'duration': data.get('duration_seconds')
            }
        except requests.exceptions.Timeout:
            print("  - 请求音频服务器超时")
            return None
        except requests.exceptions.ConnectionError:
            print("  - 无法连接音频服务器")
            return None
        except Exception as e:
            print(f"  - 请求音频服务器失败: {e}")
            return None

    def generate_summary(self, video_title, transcript_data):
        # 提取字幕文本和语言信息
        if isinstance(transcript_data, dict):
            transcript_text = transcript_data['text']
            language = transcript_data.get('language', '未知')
            language_code = transcript_data.get('language_code', '')
        else:
            # 兼容旧格式（如果直接传字符串）
            transcript_text = transcript_data
            language = '英语'
            language_code = 'en'

        prompt = f"""你将作为一名专业的金融内容总结助手，针对以下视频内容进行客观、清晰、可读性强的总结。请遵守以下要求：

【总结要求】
使用中文进行总结，并使用HTML格式输出，包含适当的标签（如<h3>、<p>、<ul>、<li>等），不要使用Markdown。

提取视频中的 核心观点、市场背景、逻辑链条

用 简洁、非技术性语言 描述复杂概念，保证客户能快速理解。

总结格式如下：

【视频要点总结】

核心观点：

分析逻辑：

引用的数据/事实：

市场背景：

潜在风险与不确定性：

博主个人观点的性质说明（可选）：

请开始总结以下内容：
视频标题：{video_title}
主要内容：{transcript_text}
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"AI总结生成失败: {e}")
            return "无法生成总结"

    def send_email(self, subject, content):
        try:
            # 添加完整的HTML文档结构
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2, h3, h4 {{
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        ul, ol {{
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""

            params = {
                "from": self.config['email']['from'],
                "to": self.config['subscribers'],
                "subject": subject,
                "html": html_content,
            }

            response = resend.Emails.send(params)
            print(f"邮件发送成功: {subject} (ID: {response['id']})")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False

    def process_video(self, channel_name, video):
        video_id = video['video_id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"处理新视频: {video['title']}")

        transcript_data = self.request_transcript_from_server(video_id)
        if not transcript_data:
            print("<p style='color: #999;'>无法获取视频内容，无法生成总结。</p>")
        else:
            summary = self.generate_summary(video['title'], transcript_data)

            email_content = f"""
        <h1 style="color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">
        【{channel_name}】发布新视频
        </h1>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p><strong>视频标题：</strong> {video['title']}</p>
        <p><strong>发布时间：</strong> {video['published_at']}</p>
        <p><strong>视频链接：</strong> <a href="{video_url}" style="color: #3498db;">{video_url}</a></p>
        </div>
        
        <hr style="border: 1px solid #ddd; margin: 30px 0;">
        
        <h2 style="color: #34495e;">内容总结</h2>
        
        <div style="margin-top: 20px;">
        {summary}
        </div>
        
        <hr style="border: 1px solid #ddd; margin: 30px 0;">
        
        <p style="color: #999; font-size: 12px; text-align: center;">
        本邮件由YouTube监控系统自动发送
        </p>
        <p style="color: #999; font-size: 12px; text-align: center;">
        Xiangzhen 
        </p>
        """

            subject = f"[YouTube总结] {channel_name} - {video['title']}"
            self.send_email(subject, email_content)

    def run(self):
        print(f"开始检查更新 - {datetime.now()}")

        all_new_videos = {}

        for channel in self.config['channels']:
            channel_id = channel['id']
            channel_name = channel['name']

            print(f"检查频道: {channel_name}")
            new_videos = self.get_channel_uploads(channel_id)

            if new_videos:
                print(f"发现 {len(new_videos)} 个新视频")
                all_new_videos[channel_id] = new_videos

                for video in new_videos:
                    self.process_video(channel_name, video)

                    if channel_id not in self.last_videos:
                        self.last_videos[channel_id] = []
                    self.last_videos[channel_id].append(video['video_id'])
            else:
                print("无新视频")

        if all_new_videos:
            self.save_json('last_videos.json', self.last_videos)
            print("状态已保存")

        print("检查完成")

    def get_video_privacy_status(self, video_ids):
        if not video_ids:
            return {}

        privacy_map = {}
        try:
            for i in range(0, len(video_ids), 50):
                chunk = video_ids[i:i + 50]
                response = self.youtube.videos().list(
                    part='status',
                    id=','.join(chunk)
                ).execute()

                for item in response.get('items', []):
                    privacy_map[item['id']] = item['status'].get('privacyStatus', 'unknown')
        except Exception as e:
            print(f"获取视频隐私状态失败: {e}")

        return privacy_map

    def filter_public_videos(self, playlist_items, privacy_map, cutoff_time, channel_id):
        filtered = []
        processed_ids = set(self.last_videos.get(channel_id, []))

        for item in playlist_items:
            video_id = item['contentDetails']['videoId']
            privacy_status = privacy_map.get(video_id, 'unknown')

            if privacy_status != 'public':
                print(f"  - 跳过非公开视频({privacy_status}): {video_id}")
                continue

            published_at = datetime.strptime(
                item['snippet']['publishedAt'],
                '%Y-%m-%dT%H:%M:%SZ'
            ).replace(tzinfo=timezone.utc)

            if published_at <= cutoff_time:
                continue

            if video_id in processed_ids:
                continue

            filtered.append({
                'video_id': video_id,
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'description': item['snippet']['description']
            })

        return filtered

if __name__ == '__main__':
    print("YouTube监控系统启动")
    print("-" * 50)

    monitor = YouTubeMonitor()
    print(f"✓ YouTubeMonitor 实例创建成功")

    monitor.run()

    print("-" * 50)
    print("运行完成")
