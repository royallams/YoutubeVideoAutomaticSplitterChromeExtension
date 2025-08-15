import logging
import os
import zipfile
from pathlib import Path

from flask import Flask, jsonify, request, send_file, url_for
from flask_cors import CORS
from pytube import YouTube
import moviepy.editor as mp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.INFO)

def download_youtube_video(url, output_path="video.mp4"):
    logging.info("Downloading video from URL: %s", url)
    yt = YouTube(url)
    title = yt.title
    stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
    if stream is None:
        raise ValueError("No suitable video stream found")
    stream.download(filename=output_path)
    logging.info("Video downloaded to %s", output_path)
    return output_path, title

def split_video(input_path, output_dir, segment_length=40):
    """Split ``input_path`` into ``segment_length`` second clips and zip them."""
    logging.info(
        "Splitting video %s into %s-second segments", input_path, segment_length
    )
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with mp.VideoFileClip(input_path) as video:
        duration = int(video.duration)
        for start in range(0, duration, segment_length):
            end = min(start + segment_length, duration)
            segment = video.subclip(start, end)
            segment_path = output_path / f"segment_{start}_{end}.mp4"
            segment.write_videofile(
                str(segment_path), codec="libx264", audio=False, logger=None
            )
            logging.info("Segment saved to %s", segment_path)

    zip_filename = output_path / "split_videos.zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for file in output_path.glob("*.mp4"):
            zipf.write(file, file.name)

    logging.info("All segments zipped into %s", zip_filename)
    return str(zip_filename)

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
        download_url = url_for("download", filename=zip_filename, _external=True)
        return jsonify({"success": True, "downloadUrl": download_url})
    except Exception as e:
        logging.error(f"Error processing video: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
