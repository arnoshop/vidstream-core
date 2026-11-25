import os
import secrets
import shutil
from fastapi import HTTPException, UploadFile, status

ALLOWED_VIDEO_EXTENSIONS = [".mp4", ".webm", ".mov", ".mkv"]


def get_media_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    media_dir = os.path.join(project_root, "media")

    if not os.path.exists(media_dir):
        os.makedirs(media_dir, exist_ok=True)

    return media_dir


def get_media_subfolder(subfolder_name):
    clean_folder = subfolder_name.strip().lower()
    if clean_folder == "" or not clean_folder.isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid storage subfolder name"
        )

    media_root = get_media_root()
    target_folder = os.path.join(media_root, clean_folder)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder, exist_ok=True)

    return target_folder


def extract_safe_extension(original_filename):
    if original_filename is None or original_filename.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename"
        )

    parts = os.path.splitext(original_filename)
    ext = parts[1].lower().strip()

    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported video format. Allowed: mp4, webm, mov, mkv"
        )

    return ext


def save_uploaded_video(upload_file: UploadFile, subfolder_name: str):
    clean_folder = subfolder_name.strip().lower()
    target_folder = get_media_subfolder(clean_folder)
    file_ext = extract_safe_extension(upload_file.filename)

    random_name = secrets.token_hex(8) + file_ext
    full_file_path = os.path.join(target_folder, random_name)

    chunk_size = 1024 * 1024

    try:
        with open(full_file_path, "wb") as output_file:
            while True:
                data_chunk = upload_file.file.read(chunk_size)
                if not data_chunk:
                    break
                output_file.write(data_chunk)
    except Exception:
        if os.path.exists(full_file_path):
            os.remove(full_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded video file"
        )
    finally:
        upload_file.file.close()

    relative_url = "/media/" + clean_folder + "/" + random_name
    return relative_url


def resolve_local_media_path(media_url):
    if media_url is None:
        return None

    cleaned_url = media_url.strip()
    if not cleaned_url.startswith("/media/"):
        return None

    prefix_len = len("/media/")
    relative_part = cleaned_url[prefix_len:]
    relative_part = relative_part.lstrip("/\\")

    if relative_part == "":
        return None

    media_root = os.path.abspath(get_media_root())
    joined_path = os.path.join(media_root, relative_part)
    target_path = os.path.abspath(joined_path)

    safe_prefix = media_root + os.sep
    if not target_path.startswith(safe_prefix):
        return None

    return target_path


def delete_local_media_file(media_url):
    target_path = resolve_local_media_path(media_url)
    if target_path is None:
        return False

    if not os.path.isfile(target_path):
        return False

    try:
        os.remove(target_path)
        return True
    except Exception:
        return False


def delete_local_hls_directory(media_url):
    if media_url is None:
        return False

    cleaned_url = media_url.strip()
    if not cleaned_url.startswith("/media/hls/"):
        return False

    target_file = resolve_local_media_path(cleaned_url)
    if target_file is None:
        return False

    hls_root = os.path.abspath(get_media_subfolder("hls"))
    hls_folder = os.path.abspath(os.path.dirname(target_file))

    safe_prefix = hls_root + os.sep
    if not hls_folder.startswith(safe_prefix):
        return False

    if not os.path.isdir(hls_folder):
        return False

    try:
        shutil.rmtree(hls_folder)
        return True
    except Exception:
        return False