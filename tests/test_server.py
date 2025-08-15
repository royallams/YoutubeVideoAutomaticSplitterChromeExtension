import os
import sys
import types
import zipfile
from pathlib import Path

# Stub out external dependencies so the module can be imported without them
class DummyVideoFileClip:
    def __init__(self, *args, **kwargs):
        self.duration = 5

    def subclip(self, start, end):
        return self

    def write_videofile(self, path, *args, **kwargs):
        Path(path).write_text("dummy")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

moviepy = types.ModuleType("moviepy")
editor = types.ModuleType("moviepy.editor")
editor.VideoFileClip = DummyVideoFileClip
moviepy.editor = editor
sys.modules.setdefault("moviepy", moviepy)
sys.modules.setdefault("moviepy.editor", editor)

flask = types.ModuleType("flask")
flask.Flask = lambda name: types.SimpleNamespace(route=lambda *a, **k: (lambda f: f))
flask.jsonify = lambda obj: obj
flask.request = types.SimpleNamespace(get_json=lambda: {})
flask.send_file = lambda filename, as_attachment=True: filename
flask.url_for = lambda endpoint, filename=None, _external=False: f"/download/{filename}"
sys.modules.setdefault("flask", flask)

flask_cors = types.ModuleType("flask_cors")
flask_cors.CORS = lambda app: None
sys.modules.setdefault("flask_cors", flask_cors)

pytube = types.ModuleType("pytube")
class DummyStream:
    def download(self, filename):
        Path(filename).write_text("video")
class DummyStreams:
    def filter(self, **kwargs):
        return self
    def first(self):
        return DummyStream()
class DummyYouTube:
    def __init__(self, url):
        self.title = "Dummy Title"
        self.streams = DummyStreams()
pytube.YouTube = DummyYouTube
sys.modules.setdefault("pytube", pytube)

sys.path.append(str(Path(__file__).resolve().parents[1]))
from youtube_splitter_server import server


def test_split_video_creates_segments_and_zip(tmp_path):
    video_path = tmp_path / "video.mp4"
    video_path.write_text("source")
    output_dir = tmp_path / "out"
    zip_path = server.split_video(str(video_path), str(output_dir), segment_length=2)

    assert os.path.exists(zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

    mp4_files = [n for n in names if n.endswith(".mp4")]
    assert len(mp4_files) == 3
    assert "split_videos.zip" not in names
