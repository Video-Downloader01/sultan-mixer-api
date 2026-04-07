from flask import Flask, request, send_file
from flask_cors import CORS
import requests
import os
import tempfile
import subprocess

app = Flask(__name__)
CORS(app) # Vercel ko allow karna

@app.route('/', methods=['GET'])
def home():
    return "🔥 Sultan Mixing Factory is Zinda!"

@app.route('/mix', methods=['POST'])
def mix():
    data = request.json
    img_url = data.get('image_url')
    audio_url = data.get('audio_url')

    if not img_url or not audio_url:
        return {"error": "Links missing"}, 400

    try:
        # Safe Temporary Folder
        temp_dir = tempfile.mkdtemp()
        img_path = os.path.join(temp_dir, 'image.jpg')
        audio_path = os.path.join(temp_dir, 'audio.mp3')
        out_path = os.path.join(temp_dir, 'sultan_post.mp4')

        # Instagram blocks se bachne ke liye headers
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        # Files download karo
        with open(img_path, 'wb') as f:
            f.write(requests.get(img_url, headers=headers).content)
        with open(audio_path, 'wb') as f:
            f.write(requests.get(audio_url, headers=headers).content)

        # THE MAGIC: Bulletproof FFmpeg Command (0% Crash Rate)
        cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', img_path, '-i', audio_path,
            '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k',
            '-pix_fmt', 'yuv420p', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
            '-shortest', out_path
        ]
        
        # Command run karna
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return send_file(out_path, as_attachment=True, download_name="Sultan_Mixed_Post.mp4", mimetype="video/mp4")
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
