import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pytube import YouTube
import moviepy.editor as mp
import os
import zipfile

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.INFO)

def download_youtube_video(url, output_path='video.mp4'):
    logging.info(f"Downloading video from URL: {url}")
    yt = YouTube(url)
    title = yt.title
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    stream.download(filename=output_path)
    logging.info(f"Video downloaded to {output_path}")
    return output_path, title

def split_video(input_path, output_dir, segment_length=40):
    logging.info(f"Splitting video {input_path} into {segment_length}-second segments")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    video = mp.VideoFileClip(input_path)
    duration = int(video.duration)
    for start in range(0, duration, segment_length):
        end = start + segment_length
        if end > duration:
            end = duration
        segment = video.subclip(start, end)
        segment_path = os.path.join(output_dir, f'segment_{start}_{end}.mp4')
        segment.write_videofile(segment_path)
        logging.info(f"Segment saved to {segment_path}")

    zip_filename = os.path.join(output_dir, "split_videos.zip")
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))
    
    logging.info(f"All segments zipped into {zip_filename}")
    return zip_filename

@app.route('/split', methods=['POST'])
def split():
    data = request.get_json()
    url = data['url']
    logging.info(f"Received split request for URL: {url}")
    try:
        video_path, title = download_youtube_video(url)
        safe_title = "_".join(title.split()[:3]).replace(" ", "_").replace("/", "_").replace("\\", "_")
        output_dir = os.path.join("Outputs", safe_title)
        zip_filename = split_video(video_path, output_dir)
        return jsonify({'success': True, 'downloadUrl': f'http://localhost:5000/download/{zip_filename}'})
    except Exception as e:
        logging.error(f"Error processing video: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
