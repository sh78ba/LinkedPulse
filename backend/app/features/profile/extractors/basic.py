import re
from typing import Any

from app.features.profile.schemas import Profile


def _get_localized_str(val: Any) -> str | None:
    """Extracts a string from either a plain string or a LinkedIn multiLocale dictionary."""
    if isinstance(val, str):
        return val.strip() or None
    if isinstance(val, dict):
        for k in ["en_US", "text", "value", "name", "localized"]:
            if k in val and isinstance(val[k], str) and val[k].strip():
                return val[k].strip()
        for v in val.values():
            if isinstance(v, str) and v.strip():
                return v.strip()
    return None


def extract_basic_profile(
    raw_entities: list[dict[str, Any]],
    html_content: str | None = None,
    public_id: str | None = None,
) -> Profile:
    """Defensively extracts basic profile details (name, headline, location, about, profile_url)."""
    name: str | None = None
    headline: str | None = None
    location: str | None = None
    about: str | None = None
    profile_url: str | None = f"https://www.linkedin.com/in/{public_id}/" if public_id else None

    # 1. Search in Voyager JSON entity payloads
    for entity in raw_entities:
        if not isinstance(entity, dict):
            continue

        entity_type = entity.get("$type", "")

        # Voyager Dash Profile entity
        is_profile = (
            "Profile" in entity_type
            or "Profile" in str(entity.get("$recipeType", ""))
            or "publicIdentifier" in entity
            or "firstName" in entity
        )

        if is_profile and entity.get("@type") != "Person":
            first_name = (
                _get_localized_str(entity.get("firstName") or entity.get("multiLocaleFirstName"))
                or ""
            )
            last_name = (
                _get_localized_str(entity.get("lastName") or entity.get("multiLocaleLastName"))
                or ""
            )
            if first_name or last_name:
                name = f"{first_name} {last_name}".strip() or name

            headline = headline or _get_localized_str(
                entity.get("headline") or entity.get("multiLocaleHeadline")
            )
            about = about or _get_localized_str(
                entity.get("summary") or entity.get("multiLocaleSummary")
            )

            # Location extraction (prioritize full localized geo name)
            loc_val = None
            if isinstance(entity.get("geoLocation"), dict):
                geo_obj = entity["geoLocation"]
                loc_val = (
                    geo_obj.get("geo", {}).get("defaultLocalizedName")
                    if isinstance(geo_obj.get("geo"), dict)
                    else None
                ) or geo_obj.get("defaultLocalizedName") or geo_obj.get("geoPlace")

            if not loc_val:
                loc_val = entity.get("locationName") or entity.get("geoCountryName")

            if not loc_val and isinstance(entity.get("location"), dict):
                loc_val = entity["location"].get("name") or entity["location"].get("countryCode")

            location = location or _get_localized_str(loc_val)



        # JSON-LD Person schema entity
        if entity.get("@type") == "Person":
            name = name or entity.get("name")
            headline = headline or entity.get("jobTitle")
            about = about or entity.get("description")
            address = entity.get("address")
            if isinstance(address, dict):
                loc_parts = [
                    address.get("addressLocality"),
                    address.get("addressRegion"),
                    address.get("addressCountry"),
                ]
                location = location or ", ".join([p for p in loc_parts if p])
            elif isinstance(address, str):
                location = location or address

    # 2. Search in HTML JSON-LD / tags if basic fields are missing
    if html_content and (not name or not headline or not about):
        # OpenGraph meta tag fallback
        og_desc = re.search(
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
            html_content,
            re.IGNORECASE,
        )
        if og_desc:
            desc_text = og_desc.group(1).strip()
            headline = headline or desc_text

        # Title tag fallback
        if not name or not headline:
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE)
            if title_match:
                title_text = title_match.group(1).strip()
                clean_title = re.sub(r"\s*\|\s*LinkedIn.*$", "", title_text, flags=re.IGNORECASE)
                if " - " in clean_title:
                    parts = clean_title.split(" - ", 1)
                    name = name or parts[0].strip()
                    headline = headline or parts[1].strip()
                else:
                    name = name or clean_title.strip()

    return Profile(
        name=name or None,
        headline=headline or None,
        location=location or None,
        about=about or None,
        profile_url=profile_url,
        images=[],
    )
