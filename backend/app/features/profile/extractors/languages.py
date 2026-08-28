from typing import Any

from app.features.profile.schemas import Language


def _get_localized_str(val: Any) -> str | None:
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


def extract_languages(raw_entities: list[dict[str, Any]]) -> list[Language]:
    """Defensively extracts spoken/written languages from LinkedIn raw entity graph."""
    languages: list[Language] = []
    seen: set[str] = set()

    for entity in raw_entities:
        if not isinstance(entity, dict):
            continue

        entity_type = entity.get("$type", "")

        is_language = (
            "Language" in entity_type or "language" in str(entity.get("entityUrn", "")).lower()
        )

        if is_language:
            name = _get_localized_str(entity.get("name") or entity.get("multiLocaleName"))
            proficiency = _get_localized_str(
                entity.get("proficiency") or entity.get("multiLocaleProficiency")
            )

            if name and name not in seen:
                seen.add(name)
                languages.append(
                    Language(
                        name=name,
                        proficiency=proficiency,
                    )
                )

    return languages
