from flask import Flask, request, send_file
from flask_cors import CORS
import requests
from moviepy.editor import ImageClip, AudioFileClip
import os
import tempfile

app = Flask(__name__)
CORS(app) # Vercel ko connect karne ki permission

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
        # Safe Temporary Folder Banana
        temp_dir = tempfile.mkdtemp()
        img_path = os.path.join(temp_dir, 'image.jpg')
        audio_path = os.path.join(temp_dir, 'audio.mp3')
        out_path = os.path.join(temp_dir, 'sultan_post.mp4')

        # 1. Instagram se Photo aur Audio download karna
        with open(img_path, 'wb') as f:
            f.write(requests.get(img_url).content)
        with open(audio_path, 'wb') as f:
            f.write(requests.get(audio_url).content)

        # 2. Dono ko Jodna (Mixing)
        audio_clip = AudioFileClip(audio_path)
        image_clip = ImageClip(img_path)
        
        # PRO TRICK: fps=1 rakhne se free server crash nahi hoga aur video 2 second me ban jayegi!
        video_clip = image_clip.set_duration(audio_clip.duration)
        video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(out_path, fps=1, codec="libx264", audio_codec="aac", logger=None)

        # 3. User ko Video wapas bhejna
        return send_file(out_path, as_attachment=True, download_name="Sultan_Mixed_Post.mp4", mimetype="video/mp4")
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
