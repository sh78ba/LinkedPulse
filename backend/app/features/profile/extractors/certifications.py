from typing import Any

from app.features.profile.schemas import Certification


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


def extract_certifications(raw_entities: list[dict[str, Any]]) -> list[Certification]:
    """Defensively extracts licenses and certifications from LinkedIn raw entity graph."""
    certifications: list[Certification] = []
    seen: set[str] = set()

    for entity in raw_entities:
        if not isinstance(entity, dict):
            continue

        entity_type = entity.get("$type", "")

        is_certification = (
            "Certification" in entity_type
            or "certification" in str(entity.get("entityUrn", "")).lower()
        )

        if is_certification:
            name = _get_localized_str(entity.get("name") or entity.get("multiLocaleName"))
            authority = _get_localized_str(
                entity.get("authority")
                or entity.get("companyName")
                or entity.get("multiLocaleAuthority")
                or (
                    entity.get("company", {}).get("name")
                    if isinstance(entity.get("company"), dict)
                    else None
                )
            )
            license_number = _get_localized_str(
                entity.get("licenseNumber") or entity.get("licenseNumberString")
            )
            url = entity.get("url")

            issue_date = None
            expiration_date = None

            time_period = entity.get("timePeriod") or entity.get("dateRange")
            if isinstance(time_period, dict):
                start = time_period.get("startDate") or time_period.get("start")
                if isinstance(start, dict):
                    issue_date = _format_date(start)

                end = time_period.get("endDate") or time_period.get("end")
                if isinstance(end, dict):
                    expiration_date = _format_date(end)

            if name or authority:
                key = f"{name}-{authority}"
                if key not in seen:
                    seen.add(key)
                    certifications.append(
                        Certification(
                            name=name,
                            authority=authority,
                            license_number=license_number,
                            url=url,
                            issue_date=issue_date,
                            expiration_date=expiration_date,
                        )
                    )

    return certifications


def _format_date(date_dict: dict[str, Any]) -> str | None:
    year = date_dict.get("year")
    month = date_dict.get("month")
    if year and month:
        return f"{month:02d}/{year}"
    elif year:
        return str(year)
    return None
