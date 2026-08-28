from typing import Any

from app.features.profile.schemas import Experience


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


def extract_experience(raw_entities: list[dict[str, Any]]) -> list[Experience]:
    """Defensively extracts work experience history from LinkedIn raw entity graph."""
    experiences: list[Experience] = []
    seen: set[tuple[str, str]] = set()

    for entity in raw_entities:
        if not isinstance(entity, dict):
            continue

        entity_type = entity.get("$type", "")

        is_position = (
            "Position" in entity_type or "position" in str(entity.get("entityUrn", "")).lower()
        )

        if is_position:
            title = _get_localized_str(entity.get("title") or entity.get("multiLocaleTitle"))
            company_name = _get_localized_str(
                entity.get("companyName") or entity.get("multiLocaleCompanyName")
            )
            if not company_name and isinstance(entity.get("company"), dict):
                company_name = _get_localized_str(entity["company"].get("name"))

            description = _get_localized_str(
                entity.get("description")
                or entity.get("summary")
                or entity.get("multiLocaleDescription")
            )
            location_name = _get_localized_str(
                entity.get("locationName") or entity.get("geoLocationName")
            )

            company_url = None
            company_urn = entity.get("companyUrn") or entity.get("company")
            if isinstance(company_urn, str) and "company:" in company_urn:
                comp_id = company_urn.split("company:")[-1]
                company_url = f"https://www.linkedin.com/company/{comp_id}/"

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
                else:
                    end_date_str = "Present"

            if title or company_name:
                key = (title or "", company_name or "")
                if key not in seen:
                    seen.add(key)
                    experiences.append(
                        Experience(
                            title=title,
                            company=company_name,
                            company_url=company_url,
                            location=location_name,
                            start_date=start_date_str,
                            end_date=end_date_str,
                            description=description,
                        )
                    )

        # JSON-LD worksFor / hasOccupation in Person schema
        if entity.get("@type") == "Person":
            works_for = entity.get("worksFor") or entity.get("hasOccupation")
            if isinstance(works_for, dict):
                works_for = [works_for]
            if isinstance(works_for, list):
                for wf in works_for:
                    if isinstance(wf, dict):
                        comp = wf.get("name")
                        role = wf.get("roleName") or wf.get("name")
                        key = (role or "", comp or "")
                        if key not in seen:
                            seen.add(key)
                            if comp and role and comp != role:
                                experiences.append(Experience(title=role, company=comp))
                            elif comp:
                                experiences.append(Experience(company=comp))

    return experiences


def _format_date(date_dict: dict[str, Any]) -> str | None:
    year = date_dict.get("year")
    month = date_dict.get("month")
    if year and month:
        return f"{month:02d}/{year}"
    elif year:
        return str(year)
    return None
