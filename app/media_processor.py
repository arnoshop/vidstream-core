import os
import secrets
import subprocess
from app.storage import get_media_subfolder


def extract_video_duration(video_file_path):
    if video_file_path is None or not os.path.isfile(video_file_path):
        return 0

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_file_path
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15
        )
    except Exception:
        return 0

    if result.returncode != 0:
        return 0

    raw_output = result.stdout.strip()
    if raw_output == "":
        return 0

    try:
        duration_float = float(raw_output)
    except ValueError:
        return 0

    if duration_float < 0:
        return 0

    duration_int = int(round(duration_float))
    return duration_int


def run_thumbnail_command(video_file_path, output_image_path, seek_seconds):
    command = [
        "ffmpeg",
        "-y",
        "-ss",
        str(seek_seconds),
        "-i",
        video_file_path,
        "-vframes",
        "1",
        "-q:v",
        "3",
        "-vf",
        "scale=640:-1",
        output_image_path
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20
        )
    except Exception:
        return False

    if result.returncode != 0:
        return False

    if not os.path.isfile(output_image_path):
        return False

    file_size = os.path.getsize(output_image_path)
    if file_size <= 0:
        return False

    return True


def generate_video_thumbnail(video_file_path, duration_seconds=0):
    if video_file_path is None or not os.path.isfile(video_file_path):
        return None

    thumb_folder = get_media_subfolder("thumbnails")
    thumb_filename = secrets.token_hex(8) + ".jpg"
    output_image_path = os.path.join(thumb_folder, thumb_filename)

    seek_time = 1
    if duration_seconds >= 6:
        seek_time = int(duration_seconds / 4)
        if seek_time > 5:
            seek_time = 5
    elif duration_seconds <= 1:
        seek_time = 0

    created = run_thumbnail_command(video_file_path, output_image_path, seek_time)

    if not created and seek_time > 0:
        created = run_thumbnail_command(video_file_path, output_image_path, 0)

    if not created:
        if os.path.exists(output_image_path):
            try:
                os.remove(output_image_path)
            except Exception:
                pass
        return None

    thumb_url = "/media/thumbnails/" + thumb_filename
    return thumb_url