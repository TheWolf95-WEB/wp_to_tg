import requests
import logging
from slugify import slugify

def upload_featured_image(image_bytes, filename, wp_url, wp_user, wp_pass):
    base = wp_url.rstrip("/") + "/wp-json/wp/v2/media"
    files = {
        "file": (filename, image_bytes.getvalue(), "image/jpeg")
    }
    resp = requests.post(base, auth=(wp_user, wp_pass), files=files)
    resp.raise_for_status()
    return resp.json()["id"]

def publish_post(title, content, media_id, wp_url, wp_user, wp_pass, category_ids=None, description=None):
    base = wp_url.rstrip("/") + "/wp-json/wp/v2"

    if category_ids is None:
        category_ids = []
    if 5 not in category_ids:
        category_ids.append(5)  # категория "Новости" по умолчанию

    slug = slugify(title)[:60]  # ЧПУ до 60 символов

    payload = {
        "title": title,
        "slug": slug,
        "content": content,
        "status": "publish",
        "featured_media": media_id,
        "categories": category_ids,
        "meta": {
            "yoast_wpseo_primary_category": category_ids[0],
            "yoast_wpseo_title": f"{title} | NDZONE",
            "yoast_wpseo_metadesc": description or "Читай все последние игровые новости и слухи на NDZONE."
        }
    }

    resp = requests.post(f"{base}/posts", auth=(wp_user, wp_pass), json=payload)
    resp.raise_for_status()
    return resp.json().get("link")

def get_all_categories(wp_url, wp_user, wp_pass):
    resp = requests.get(
        f"{wp_url.rstrip('/')}/wp-json/wp/v2/categories?per_page=100",
        auth=(wp_user, wp_pass)
    )
    resp.raise_for_status()
    return resp.json()
