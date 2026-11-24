import secrets
from xml.sax.saxutils import escape


def generate_slug(title_text):
    lowered = title_text.lower().strip()
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    slug_parts = []
    last_was_dash = False

    for ch in lowered:
        if ch in allowed_chars:
            slug_parts.append(ch)
            last_was_dash = False
        elif ch == " " or ch == "-" or ch == "_":
            if not last_was_dash and len(slug_parts) > 0:
                slug_parts.append("-")
                last_was_dash = True

    base_slug = "".join(slug_parts)
    base_slug = base_slug.strip("-")

    if base_slug == "":
        base_slug = "video"

    if len(base_slug) > 60:
        base_slug = base_slug[:60].strip("-")

    random_part = secrets.token_hex(3)
    final_slug = base_slug + "-" + random_part
    return final_slug


def build_vast_xml(ad_id, campaign_name, video_url, click_url, skip_seconds):
    safe_title = escape(str(campaign_name))
    safe_video_url = str(video_url).replace("]]>", "")
    safe_click_url = str(click_url).replace("]]>", "")

    secs = int(skip_seconds)
    if secs < 0:
        secs = 0

    if secs < 10:
        sec_text = "0" + str(secs)
    else:
        sec_text = str(secs)

    skip_offset_attr = ""
    if secs > 0:
        skip_offset_attr = ' skipoffset="00:00:' + sec_text + '"'

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<VAST version="3.0">')
    lines.append('  <Ad id="' + str(ad_id) + '">')
    lines.append('    <InLine>')
    lines.append('      <AdSystem>VidStreamCore</AdSystem>')
    lines.append('      <AdTitle>' + safe_title + '</AdTitle>')
    lines.append('      <Creatives>')
    lines.append('        <Creative>')
    lines.append('          <Linear' + skip_offset_attr + '>')
    lines.append('            <Duration>00:00:15</Duration>')
    lines.append('            <VideoClicks>')
    lines.append('              <ClickThrough><![CDATA[' + safe_click_url + ']]></ClickThrough>')
    lines.append('            </VideoClicks>')
    lines.append('            <MediaFiles>')
    lines.append('              <MediaFile delivery="progressive" type="video/mp4" width="1280" height="720">')
    lines.append('                <![CDATA[' + safe_video_url + ']]>')
    lines.append('              </MediaFile>')
    lines.append('            </MediaFiles>')
    lines.append('          </Linear>')
    lines.append('        </Creative>')
    lines.append('      </Creatives>')
    lines.append('    </InLine>')
    lines.append('  </Ad>')
    lines.append('</VAST>')

    xml_output = "\n".join(lines)
    return xml_output