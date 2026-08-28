from typing import Any

from app.features.profile.schemas import Education


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


def extract_education(raw_entities: list[dict[str, Any]]) -> list[Education]:
    """Defensively extracts educational history from LinkedIn raw entity graph."""
    education_list: list[Education] = []
    seen: set[tuple[str, str]] = set()

    for entity in raw_entities:
        if not isinstance(entity, dict):
            continue

        entity_type = entity.get("$type", "")

        is_education = (
            "Education" in entity_type or "education" in str(entity.get("entityUrn", "")).lower()
        )

        if is_education:
            school_name = _get_localized_str(
                entity.get("schoolName")
                or entity.get("multiLocaleSchoolName")
                or (
                    entity.get("school", {}).get("name")
                    if isinstance(entity.get("school"), dict)
                    else None
                )
            )
            degree_name = _get_localized_str(
                entity.get("degreeName") or entity.get("multiLocaleDegreeName")
            )
            field_of_study = _get_localized_str(
                entity.get("fieldOfStudy") or entity.get("multiLocaleFieldOfStudy")
            )
            description = _get_localized_str(entity.get("description") or entity.get("activities"))

            start_date_str = None
            end_date_str = None

            time_period = entity.get("timePeriod") or entity.get("dateRange")
            if isinstance(time_period, dict):
                start = time_period.get("startDate") or time_period.get("start")
                if isinstance(start, dict):
                    start_date_str = _format_date(start)

                end = time_period.get("endDate") or time_period.get("end")
                if isinstance(end, dict):
                    end_date_str = _format_date(end)

            if school_name or degree_name or field_of_study:
                key = (school_name or "", degree_name or "")
                if key not in seen:
                    seen.add(key)
                    education_list.append(
                        Education(
                            school=school_name,
                            degree=degree_name,
                            field_of_study=field_of_study,
                            start_date=start_date_str,
                            end_date=end_date_str,
                            description=description,
                        )
                    )

        # JSON-LD alumniOf in Person schema
        if entity.get("@type") == "Person":
            alumni_of = entity.get("alumniOf")
            if isinstance(alumni_of, dict):
                alumni_of = [alumni_of]
            if isinstance(alumni_of, list):
                for alum in alumni_of:
                    school = None
                    if isinstance(alum, dict):
                        school = alum.get("name")
                    elif isinstance(alum, str):
                        school = alum
                    if school:
                        key = (school, "")
                        if key not in seen:
                            seen.add(key)
                            education_list.append(Education(school=school))

    return education_list


def _format_date(date_dict: dict[str, Any]) -> str | None:
    year = date_dict.get("year")
    month = date_dict.get("month")
    if year and month:
        return f"{month:02d}/{year}"
    elif year:
        return str(year)
    return None
