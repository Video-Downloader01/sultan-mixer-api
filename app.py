from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import os
import tempfile
import subprocess

app = Flask(__name__)
# Vercel ko 100% connect hone ki permission
CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.route('/', methods=['GET'])
def home():
    return "🔥 Sultan Mixing Factory is Zinda!"

@app.route('/mix', methods=['POST', 'OPTIONS'])
def mix():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json
        img_url = data.get('image_url')
        audio_url = data.get('audio_url')

        if not img_url or not audio_url:
            return jsonify({"success": False, "error": "Links missing"}), 400

        temp_dir = tempfile.mkdtemp()
        img_path = os.path.join(temp_dir, 'image.jpg')
        audio_path = os.path.join(temp_dir, 'audio.mp3')
        out_path = os.path.join(temp_dir, 'sultan_post.mp4')

        # Instagram ko block karne se rokne ke liye
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        r_img = requests.get(img_url, headers=headers)
        r_aud = requests.get(audio_url, headers=headers)
        
        # Agar link expire ho gaya ho toh user ko batana
        if r_img.status_code != 200 or r_aud.status_code != 200:
            return jsonify({"success": False, "error": "Link expire ho gaya, dubara paste karein!"}), 400

        with open(img_path, 'wb') as f: f.write(r_img.content)
        with open(audio_path, 'wb') as f: f.write(r_aud.content)

        # BRAHMASTRA COMMAND (Forces Even Dimensions to stop crash)
        cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', img_path, '-i', audio_path,
            '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k',
            '-pix_fmt', 'yuv420p', 
            '-vf', "scale=trunc(iw/2)*2:trunc(ih/2)*2", 
            '-shortest', out_path
        ]
        
        # Command run karna
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if process.returncode != 0:
            return jsonify({"success": False, "error": "Video banne mein dikkat aayi."}), 500

        return send_file(out_path, as_attachment=True, download_name="Sultan_Mixed_Post.mp4", mimetype="video/mp4")
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)[:100]}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
