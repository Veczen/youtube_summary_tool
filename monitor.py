import json
import os
import requests
import logging
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
import google.generativeai as genai
import resend


class YouTubeMonitor:
    def __init__(self):
        self.config = self.load_json('config.json')
        self.last_videos = self.load_json('last_videos.json')
        self.pending_jobs = self.load_json('pending_jobs.json')  # 新增：跟踪待处理任务

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

    def delete_audio_file(self, video_id):
        """删除音频文件"""
        if not self.audio_server_url:
            return False

        # Validate video_id to prevent path traversal attacks
        # YouTube video IDs are 11 characters, alphanumeric with - and _
        import re
        if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
            print(f"  - 无效的视频ID格式: {video_id}")
            return False

        base_url = self.audio_server_url.rstrip('/')
        headers = {
            'Content-Type': 'application/json'
        }
        if self.audio_server_api_key:
            headers['X-API-Key'] = self.audio_server_api_key

        delete_url = f"{base_url}/transcribe/by-video/{video_id}"
        try:
            response = requests.delete(delete_url, headers=headers, timeout=15)
            if response.status_code in (200, 204):
                print(f"  ✓ 音频文件已删除: {video_id}")
                return True
            elif response.status_code == 404:
                # 文件不存在或已被删除，这对于清理操作来说是可接受的
                # 可能的原因：文件已被手动删除，或从未创建成功
                print(f"  - 音频文件不存在或已删除: {video_id}")
                return True
            else:
                print(f"  - 删除音频文件失败: HTTP {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            print(f"  - 删除音频文件超时: {video_id}")
            return False
        except requests.exceptions.ConnectionError:
            print(f"  - 无法连接到服务器删除音频文件: {video_id}")
            return False
        except Exception as e:
            print(f"  - 删除音频文件异常 ({video_id}): {type(e).__name__}: {e}")
            return False

    def check_transcription_status(self, video_id):
        """检查转录任务是否已完成，返回转录文本或 None"""
        if not self.audio_server_url:
            return None

        base_url = self.audio_server_url.rstrip('/')
        headers = {
            'Content-Type': 'application/json'
        }
        if self.audio_server_api_key:
            headers['X-API-Key'] = self.audio_server_api_key

        query_url = f"{base_url}/transcribe/by-video/{video_id}"
        try:
            response = requests.get(query_url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                state = data.get('state')

                if state == 'done':
                    text = data.get('text', '').strip()
                    if text:
                        print(f"  ✓ 视频 {video_id} 转录已完成")
                        return {
                            'text': text,
                            'language': data.get('language', 'auto'),
                            'language_code': data.get('language_code', 'auto'),
                            'duration': data.get('duration_seconds')
                        }
                    else:
                        print(f"  - 视频 {video_id} 转录文本为空")
                        return None
                elif state == 'pending':
                    print(f"  - 视频 {video_id} 转录任务等待中...")
                    return None
                elif state == 'running':
                    print(f"  - 视频 {video_id} 转录任务运行中...")
                    return None
                elif state == 'error':
                    error_msg = data.get('error', '未知错误')
                    print(f"  ✗ 视频 {video_id} 转录失败: {error_msg}")
                    return None
            elif response.status_code == 404:
                # 任务不存在
                print(f"  - 视频 {video_id} 的转录任务不存在")
                return None
            else:
                print(f"  - 查询转录状态失败: HTTP {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print(f"  - 查询转录状态超时")
            return None
        except requests.exceptions.ConnectionError:
            print(f"  - 无法连接到转录服务器 {base_url}")
            return None
        except Exception as e:
            print(f"  - 查询转录状态异常: {type(e).__name__}: {e}")
            return None

    def submit_transcription_job(self, video_id, video_url):
        """提交转录任务（不等待完成）"""
        if not self.audio_server_url:
            print("  - 未配置 AUDIO_SERVER_URL，无法提交转录任务")
            return False

        base_url = self.audio_server_url.rstrip('/')
        headers = {
            'Content-Type': 'application/json'
        }
        if self.audio_server_api_key:
            headers['X-API-Key'] = self.audio_server_api_key

        submit_url = f"{base_url}/transcribe"
        payload = {'url': video_url}

        try:
            print(f"  - 提交转录任务: {video_id}")
            # 提交任务只是加入队列，应该很快返回，但考虑到网络延迟和可能的并发，设置较长超时
            response = requests.post(submit_url, json=payload, headers=headers, timeout=60)

            if response.status_code in (200, 202):
                data = response.json()
                job_id = data.get('job_id')
                state = data.get('state')
                queue_size = data.get('queue_size', '?')
                print(f"  ✓ 任务已提交 (job_id={job_id}, state={state}, 队列={queue_size})")
                return True
            else:
                print(f"  - 提交转录任务失败: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"  - 错误详情: {error_data.get('error', '未知错误')}")
                except:
                    pass
                return False
        except requests.exceptions.Timeout:
            print(f"  - 提交超时（60秒），但任务可能已加入队列")
            return True  # 返回 True，允许继续处理其他视频
        except requests.exceptions.ConnectionError:
            print(f"  - 无法连接到服务器 {base_url}")
            return False
        except Exception as e:
            print(f"  - 提交转录任务异常: {type(e).__name__}: {e}")
            return False

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

    def process_video(self, channel_name, video, is_new=False):
        """
        处理视频：
        - is_new=False: 检查已提交的转录任务是否完成，完成则生成总结并发送邮件
        - is_new=True: 提交新的转录任务（不等待）
        """
        video_id = video['video_id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        if is_new:
            # 新视频：提交转录任务
            print(f"发现新视频: {video['title']}")
            success = self.submit_transcription_job(video_id, video_url)

            if success:
                # 添加到待处理列表（保存完整的视频信息）
                self.pending_jobs[video_id] = {
                    'video_url': video_url,
                    'video_title': video.get('title', ''),
                    'channel_name': channel_name,
                    'published_at': video.get('published_at', ''),
                    'description': video.get('description', ''),
                    'submitted_at': datetime.now().isoformat()
                }
                print(f"  ✓ 视频已加入待处理队列")
            else:
                print(f"  ✗ 提交转录任务失败，将在下次重试")
        else:
            # 旧视频：检查转录是否完成
            print(f"检查待处理视频: {video.get('title', video_id)}")
            transcript_data = self.check_transcription_status(video_id)

            if transcript_data:
                # 转录完成，生成总结并发送邮件
                print(f"  ✓ 转录已完成，开始生成总结...")
                summary = self.generate_summary(video.get('title', ''), transcript_data)

                email_content = f"""
<h1 style="color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">
    【{channel_name}】发布新视频
</h1>
        
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
<p><strong>视频标题：</strong> {video.get('title', '')}</p>
<p><strong>发布时间：</strong> {video.get('published_at', '')}</p>
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

                subject = f"[YouTube总结] {channel_name} - {video.get('title', '')}"
                if self.send_email(subject, email_content):
                    print(f"  ✓ 邮件发送成功")
                    
                    # 删除音频文件
                    self.delete_audio_file(video_id)
                    
                    # 从待处理列表中移除
                    if video_id in self.pending_jobs:
                        del self.pending_jobs[video_id]

                    # 标记为已处理
                    channel_id = self.get_channel_id_by_name(channel_name)
                    if channel_id:
                        if channel_id not in self.last_videos:
                            self.last_videos[channel_id] = []
                        if video_id not in self.last_videos[channel_id]:
                            self.last_videos[channel_id].append(video_id)
                else:
                    print(f"  ✗ 邮件发送失败")
            else:
                # 转录未完成或失败，保持在待处理列表中，不发送邮件
                print(f"  - 转录尚未完成，保持在待处理队列中")

    def get_channel_id_by_name(self, channel_name):
        """根据频道名称获取频道ID"""
        for channel in self.config.get('channels', []):
            if channel.get('name') == channel_name:
                return channel.get('id')
        return None

    def run(self):
        print(f"开始检查更新 - {datetime.now()}")

        # 第一步：处理待处理队列中的视频（检查转录是否完成）
        if self.pending_jobs:
            print(f"\n检查待处理队列 ({len(self.pending_jobs)} 个视频)")
            print("-" * 50)

            # 复制一份待处理列表（避免在迭代时修改字典）
            pending_items = list(self.pending_jobs.items())

            for video_id, job_info in pending_items:
                video = {
                    'video_id': video_id,
                    'title': job_info.get('video_title', ''),  # 使用 video_title
                    'published_at': job_info.get('published_at', ''),
                    'description': job_info.get('description', ''),  # 添加 description
                    'video_url': job_info.get('video_url', '')
                }
                channel_name = job_info.get('channel_name', '未知频道')

                # 调试日志
                print(f"  [调试] video_id={video_id}")
                print(f"  [调试] title={video.get('title', 'N/A')}")
                print(f"  [调试] published_at={video.get('published_at', 'N/A')}")
                print(f"  [调试] channel_name={channel_name}")

                self.process_video(channel_name, video, is_new=False)

            print("-" * 50)

        # 第二步：检查各频道是否有新视频
        print(f"\n检查新视频更新")
        print("-" * 50)

        for channel in self.config['channels']:
            channel_id = channel['id']
            channel_name = channel['name']

            print(f"\n检查频道: {channel_name}")
            new_videos = self.get_channel_uploads(channel_id)

            if new_videos:
                print(f"发现 {len(new_videos)} 个新视频")

                for video in new_videos:
                    # 提交新的转录任务
                    self.process_video(channel_name, video, is_new=True)

                    # 立即标记为已处理（避免重复提交）
                    if channel_id not in self.last_videos:
                        self.last_videos[channel_id] = []
                    if video['video_id'] not in self.last_videos[channel_id]:
                        self.last_videos[channel_id].append(video['video_id'])
            else:
                print("无新视频")

        # 第三步：保存状态
        self.save_json('last_videos.json', self.last_videos)
        self.save_json('pending_jobs.json', self.pending_jobs)
        print("\n状态已保存")
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
