from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.media_processor import (
    convert_video_to_hls,
    extract_video_duration,
    generate_video_thumbnail
)
from app.models import Video
from app.storage import (
    delete_local_hls_directory,
    delete_local_media_file,
    resolve_local_media_path
)

TaskSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def process_uploaded_video_task(video_id, raw_stream_url, fallback_duration):
    local_video_path = resolve_local_media_path(raw_stream_url)
    if local_video_path is None:
        return

    probed_duration = extract_video_duration(local_video_path)
    if probed_duration > 0:
        final_duration = probed_duration
    else:
        final_duration = fallback_duration

    generated_thumb_url = generate_video_thumbnail(local_video_path, final_duration)
    hls_stream_url = convert_video_to_hls(local_video_path)

    if hls_stream_url is not None:
        final_stream_url = hls_stream_url
    else:
        final_stream_url = raw_stream_url

    db = TaskSessionLocal()
    try:
        video_item = (
            db.query(Video)
            .filter(Video.id == video_id)
            .first()
        )

        if video_item is None:
            if hls_stream_url is not None:
                delete_local_hls_directory(hls_stream_url)
            delete_local_media_file(generated_thumb_url)
            delete_local_media_file(raw_stream_url)
            return

        video_item.stream_url = final_stream_url
        video_item.thumbnail_url = generated_thumb_url
        video_item.duration_seconds = final_duration
        video_item.is_active = True

        db.commit()

        if hls_stream_url is not None:
            delete_local_media_file(raw_stream_url)
    except Exception:
        db.rollback()
        if hls_stream_url is not None:
            delete_local_hls_directory(hls_stream_url)
        delete_local_media_file(generated_thumb_url)
    finally:
        db.close()