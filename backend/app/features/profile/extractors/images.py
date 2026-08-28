import json
import re
from typing import Any


def extract_images(
    raw_entities: list[dict[str, Any]],
    html_content: str | None = None,
) -> list[str]:
    """Defensively extracts profile image URLs (avatars, banners) from Voyager entities & HTML."""
    image_urls: set[str] = set()

    # 1. Search Voyager entities for VectorImage objects
    for entity in raw_entities:
        if not isinstance(entity, dict):
            continue

        # Look for picture or displayImage structures
        for key in ["picture", "displayImage", "photo", "profilePicture", "photoFilterPicture"]:
            pic = entity.get(key)
            if isinstance(pic, dict):
                urls = _extract_urls_from_vector(pic)
                image_urls.update(urls)

        # JSON-LD Person image
        if entity.get("@type") == "Person":
            img = entity.get("image")
            if isinstance(img, str) and img.startswith("http"):
                image_urls.add(img)
            elif isinstance(img, dict):
                c_url = img.get("contentUrl") or img.get("url")
                if isinstance(c_url, str) and c_url.startswith("http"):
                    image_urls.add(c_url)

    # 2. Search HTML for og:image meta tag & schema images
    if html_content:
        og_match = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            html_content,
            re.IGNORECASE,
        )
        if not og_match:
            og_match = re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                html_content,
                re.IGNORECASE,
            )
        if og_match:
            img_url = og_match.group(1).strip()
            if img_url and img_url.startswith("http"):
                image_urls.add(img_url)

        # Search JSON-LD
        ld_match = re.search(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html_content,
            re.DOTALL | re.IGNORECASE,
        )
        if ld_match:
            try:
                ld_data = json.loads(ld_match.group(1).strip())
                if isinstance(ld_data, dict):
                    image_field = ld_data.get("image")
                    if isinstance(image_field, str) and image_field.startswith("http"):
                        image_urls.add(image_field)
                    elif isinstance(image_field, dict):
                        content_url = image_field.get("contentUrl") or image_field.get("url")
                        if content_url and isinstance(content_url, str):
                            image_urls.add(content_url)
            except Exception:
                pass

    return list(image_urls)


def _extract_urls_from_vector(vector_dict: dict[str, Any]) -> list[str]:
    urls: list[str] = []

    # Unwrap nested displayImageReference or vectorImage
    if "displayImageReference" in vector_dict and isinstance(
        vector_dict["displayImageReference"], dict
    ):
        vector_dict = vector_dict["displayImageReference"]
    if "vectorImage" in vector_dict and isinstance(vector_dict["vectorImage"], dict):
        vector_dict = vector_dict["vectorImage"]

    root_url = vector_dict.get("rootUrl", "")
    artifacts = vector_dict.get("artifacts", [])

    if isinstance(artifacts, list):
        for art in artifacts:
            if isinstance(art, dict):
                segment = art.get("fileIdentifyingUrlPathSegment") or art.get(
                    "fileSelectingUrlPathSegment"
                )
                if segment:
                    urls.append(f"{root_url}{segment}")


    # Fallback to direct url fields
    direct_url = vector_dict.get("url") or vector_dict.get("croppedImage")
    if isinstance(direct_url, str):
        urls.append(direct_url)

    return urls
