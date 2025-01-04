from flask import Flask, render_template, request, send_file
import edge_tts
import asyncio
import os
import time
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        voice = request.form['voice']
        
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'output_{timestamp}.mp3'
        filepath = os.path.join('static', filename)
        
        # 清理旧文件（删除30分钟前的文件）
        cleanup_old_files()
        
        # 生成新的音频文件
        communicate = edge_tts.Communicate(text, voice)
        asyncio.run(communicate.save(filepath))
        
        return {'status': 'success', 'audio_path': f'static/{filename}'}
    
    # 获取可用的声音列表
    voices = asyncio.run(edge_tts.list_voices())
    chinese_voices = [v for v in voices if 'zh' in v['Locale']]
    return render_template('index.html', voices=chinese_voices)

def cleanup_old_files(max_age_minutes=30):
    """删除指定时间之前的音频文件"""
    static_dir = 'static'
    current_time = time.time()
    
    # 确保static目录存在
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # 遍历static目录中的文件
    for filename in os.listdir(static_dir):
        if filename.startswith('output_') and filename.endswith('.mp3'):
            filepath = os.path.join(static_dir, filename)
            # 获取文件的最后修改时间
            file_time = os.path.getmtime(filepath)
            # 如果文件超过指定时间，则删除
            if current_time - file_time > (max_age_minutes * 60):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error deleting file {filepath}: {e}")

if __name__ == '__main__':
    app.run(debug=True)