from typing import Any

from app.features.profile.schemas import Skill


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


def extract_skills(raw_entities: list[dict[str, Any]]) -> list[Skill]:
    """Defensively extracts listed skills from LinkedIn raw entity graph."""
    skills: list[Skill] = []
    seen_skills: set[str] = set()

    for entity in raw_entities:
        if not isinstance(entity, dict):
            continue

        entity_type = entity.get("$type", "")

        is_skill = "Skill" in entity_type or "skill" in str(entity.get("entityUrn", "")).lower()

        if is_skill:
            name = _get_localized_str(
                entity.get("name")
                or entity.get("multiLocaleName")
                or (
                    entity.get("skill", {}).get("name")
                    if isinstance(entity.get("skill"), dict)
                    else None
                )
            )

            if name:
                clean_name = name.strip()
                if clean_name and clean_name.lower() not in seen_skills:
                    seen_skills.add(clean_name.lower())
                    skills.append(Skill(name=clean_name))

    return skills
