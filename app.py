from flask import Flask, render_template, request, send_file
import edge_tts
import asyncio
import os
import time
from datetime import datetime
from utils.oss_helper import OssHelper
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
oss = OssHelper()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            text = request.form['text']
            voice = request.form['voice']
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'output_{timestamp}.mp3'
            filepath = os.path.join('static', filename)
            
            # 确保static目录存在
            os.makedirs('static', exist_ok=True)
            
            # 生成新的音频文件
            communicate = edge_tts.Communicate(text, voice)
            asyncio.run(communicate.save(filepath))
            
            try:
                # 上传到OSS
                oss_path = f'audio/{filename}'
                audio_url = oss.upload_file(filepath, oss_path)
                
                # 删除本地文件
                os.remove(filepath)
                
                return {'status': 'success', 'audio_path': audio_url}
            except Exception as e:
                print(f"OSS上传失败: {str(e)}")
                # 如果OSS上传失败，返回本地文件路径
                return {'status': 'success', 'audio_path': f'static/{filename}'}
            
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return {'status': 'error', 'message': str(e)}, 500
    
    # 获取可用的声音列表
    voices = asyncio.run(edge_tts.list_voices())
    chinese_voices = [v for v in voices if 'zh' in v['Locale']]
    return render_template('index.html', voices=chinese_voices)

if __name__ == '__main__':
    app.run(debug=True)