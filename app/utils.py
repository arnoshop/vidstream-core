import secrets


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