import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import resend
import yt_dlp
import azure.cognitiveservices.speech as speechsdk

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

            new_videos = []
            for item in playlist_response.get('items', []):
                video_id = item['contentDetails']['videoId']
                published_at = datetime.strptime(
                    item['snippet']['publishedAt'],
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)

                if published_at > cutoff_time and video_id not in self.last_videos.get(channel_id, []):
                    new_videos.append({
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'published_at': item['snippet']['publishedAt'],
                        'description': item['snippet']['description']
                    })

            return new_videos
        except Exception as e:
            print(f"获取频道 {channel_id} 视频失败: {e}")
            return []

    def get_transcript(self, video_id):
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)

            transcript_obj = None

            # 策略1: 优先获取手动创建的字幕
            try:
                # 尝试获取手动创建的非英语字幕（通常是视频原始语言）
                manual_transcripts = [t for t in transcript_list if not t.is_generated]

                if manual_transcripts:
                    # 优先选择非英语的字幕
                    non_english = [t for t in manual_transcripts if not t.language_code.startswith('en')]
                    if non_english:
                        transcript_obj = non_english[0]
                        print(f"  - 找到原始语言手动字幕: {transcript_obj.language} ({transcript_obj.language_code})")
                    else:
                        # 如果只有英语手动字幕，就用英语
                        transcript_obj = manual_transcripts[0]
                        print(f"  - 使用英语手动字幕: {transcript_obj.language} ({transcript_obj.language_code})")
            except:
                pass

            # 策略2: 如果没有手动字幕，获取自动生成的字幕
            if not transcript_obj:
                available_transcripts = list(transcript_list)
                if available_transcripts:
                    # 同样优先选择非英语的自动字幕
                    non_english_auto = [t for t in available_transcripts if not t.language_code.startswith('en')]
                    if non_english_auto:
                        transcript_obj = non_english_auto[0]
                        print(f"  - 使用原始语言自动字幕: {transcript_obj.language} ({transcript_obj.language_code})")
                    else:
                        transcript_obj = available_transcripts[0]
                        print(f"  - 使用自动字幕: {transcript_obj.language} ({transcript_obj.language_code})")
                else:
                    print(f"  - 没有可用字幕")
                    return None

            # 获取字幕内容
            transcript = transcript_obj.fetch()

            # 拼接字幕文本 - 使用属性访问而非字典访问
            full_text = ' '.join([item.text for item in transcript])

            # 限制长度，避免超过API限制（Gemini 2.5 Flash支持较大输入）
            max_length = 100000  # 约100K字符，足够处理大部分视频
            return {
                'text': full_text[:max_length],
                'language': transcript_obj.language,
                'language_code': transcript_obj.language_code
            }
        except Exception as e:
            print(f"  - 获取字幕失败: {e}")
            return None

    def download_audio(self, video_id):
        """下载YouTube视频的音频"""
        try:
            print(f"  - 尝试下载音频...")

            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, f"{video_id}")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }

            video_url = f"https://www.youtube.com/watch?v={video_id}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            audio_file = f"{output_path}.wav"

            if os.path.exists(audio_file):
                print(f"  - 音频下载成功: {audio_file}")
                return audio_file
            else:
                print(f"  - 音频文件未找到")
                return None

        except Exception as e:
            print(f"  - 下载音频失败: {e}")
            return None

    def transcribe_audio_with_azure(self, audio_file):
        """使用Azure Speech SDK将音频转为文本"""
        try:
            print(f"  - 使用Azure Speech API转录音频...")

            # 从环境变量获取Azure配置
            speech_key = os.getenv('AZURE_SPEECH_KEY')
            speech_region = os.getenv('AZURE_SPEECH_REGION')

            if not speech_key or not speech_region:
                print(f"  - Azure Speech配置未找到")
                return None

            # 配置语音识别
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)

            # 设置识别语言为中文和英文（自动检测）
            auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                languages=["zh-CN", "en-US"]
            )

            audio_config = speechsdk.audio.AudioConfig(filename=audio_file)

            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                auto_detect_source_language_config=auto_detect_source_language_config,
                audio_config=audio_config
            )

            # 收集识别结果
            all_results = []
            done = False

            def stop_cb(evt):
                nonlocal done
                done = True

            def recognized_cb(evt):
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    all_results.append(evt.result.text)
                    print(f"  - 已识别片段: {len(evt.result.text)} 字符")

            # 连接事件处理器
            speech_recognizer.recognized.connect(recognized_cb)
            speech_recognizer.session_stopped.connect(stop_cb)
            speech_recognizer.canceled.connect(stop_cb)

            # 开始连续识别
            print(f"  - 开始连续语音识别...")
            speech_recognizer.start_continuous_recognition()

            # 等待识别完成（最多等待20分钟，适应长视频）
            import time
            timeout = 1200  # 20分钟
            start_time = time.time()

            while not done and (time.time() - start_time) < timeout:
                time.sleep(0.5)

            speech_recognizer.stop_continuous_recognition()

            if all_results:
                full_text = ' '.join(all_results)
                print(f"  - 转录成功，共 {len(full_text)} 个字符")
                max_length = 30000  # 约30K字符
                return {
                    'text': full_text[:max_length],
                    'language': '自动检测',
                    'language_code': 'auto'
                }
            else:
                print(f"  - 转录未产生结果")
                return None

        except Exception as e:
            print(f"  - Azure转录失败: {e}")
            return None
        finally:
            # 清理音频文件
            try:
                if audio_file and os.path.exists(audio_file):
                    os.remove(audio_file)
                    # 尝试删除临时目录
                    temp_dir = os.path.dirname(audio_file)
                    if os.path.exists(temp_dir):
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

    def get_transcript_with_fallback(self, video_id):
        """获取视频文本，优先使用字幕，失败则使用音频转录"""
        # 首先尝试获取字幕
        transcript_data = self.get_transcript(video_id)

        if transcript_data:
            return transcript_data

        # 字幕获取失败，尝试下载音频并转录
        print(f"  - 字幕不可用，尝试使用音频转录...")
        audio_file = self.download_audio(video_id)

        if audio_file:
            transcript_data = self.transcribe_audio_with_azure(audio_file)
            if transcript_data:
                return transcript_data

        print(f"  - 所有文本获取方法均失败")
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

        transcript_data = self.get_transcript_with_fallback(video_id)
        if not transcript_data:
            summary = "<p style='color: #999;'>无法获取视频内容，无法生成总结。</p>"
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

if __name__ == '__main__':
    print("YouTube监控系统启动")
    print("-" * 50)

    monitor = YouTubeMonitor()
    monitor.run()

    print("-" * 50)
    print("运行完成")
