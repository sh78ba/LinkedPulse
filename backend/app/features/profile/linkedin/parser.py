import json
import re
from typing import Any

from app.core.exceptions import LinkedInResponseParseError
from app.core.logging import get_logger
from app.features.profile.extractors.basic import extract_basic_profile
from app.features.profile.extractors.certifications import extract_certifications
from app.features.profile.extractors.education import extract_education
from app.features.profile.extractors.experience import extract_experience
from app.features.profile.extractors.images import extract_images
from app.features.profile.extractors.languages import extract_languages
from app.features.profile.extractors.skills import extract_skills
from app.features.profile.linkedin.models import LinkedInProfilePayload
from app.features.profile.schemas import ProfileResponse

logger = get_logger("linkedin_parser")


class LinkedInParser:
    """Master parser for orchestrating feature extraction from LinkedIn payload structures."""

    def parse(self, payload: LinkedInProfilePayload) -> ProfileResponse:
        """Parses a LinkedInProfilePayload into a strongly typed ProfileResponse."""
        logger.info("profile_parse_started", public_id=payload.public_id)

        try:
            raw_entities = self._collect_raw_entities(payload)
            html_content = payload.html_response.html_content if payload.html_response else None

            logger.info(
                "collected_entities_summary",
                count=len(raw_entities),
                entity_types=[
                    e.get("$type") or e.get("@type") or list(e.keys())[:3]
                    for e in raw_entities[:15]
                ],
            )

            # 1. Extract Basic Profile
            profile = extract_basic_profile(
                raw_entities=raw_entities,
                html_content=html_content,
                public_id=payload.public_id,
            )

            # 2. Extract Images
            images = extract_images(raw_entities=raw_entities, html_content=html_content)
            profile.images = images

            # 3. Extract Work Experience
            experience = extract_experience(raw_entities)

            # 4. Extract Education
            education = extract_education(raw_entities)

            # 5. Extract Skills
            skills = extract_skills(raw_entities)

            # 6. Extract Certifications
            certifications = extract_certifications(raw_entities)

            # 7. Extract Languages
            languages = extract_languages(raw_entities)

            logger.info("profile_parse_completed", public_id=payload.public_id)

            return ProfileResponse(
                success=True,
                profile=profile,
                experience=experience,
                education=education,
                skills=skills,
                certifications=certifications,
                languages=languages,
            )

        except Exception as exc:
            logger.error("profile_parse_failed", public_id=payload.public_id, error=str(exc))
            raise LinkedInResponseParseError(
                f"Error parsing profile data for '{payload.public_id}': {str(exc)}"
            ) from exc

    def _collect_raw_entities(self, payload: LinkedInProfilePayload) -> list[dict[str, Any]]:
        """Aggregates all JSON entities from Dash, ProfileView, and HTML embedded <code> tags."""
        entities: list[dict[str, Any]] = []

        # 1. Collect entities from Dash API response
        if payload.dash_response and payload.dash_response.json_data:
            data = payload.dash_response.json_data
            if "included" in data and isinstance(data["included"], list):
                entities.extend(data["included"])
            if "data" in data and isinstance(data["data"], dict):
                entities.append(data["data"])
            if "elements" in data and isinstance(data["elements"], list):
                for el in data["elements"]:
                    if isinstance(el, dict):
                        entities.append(el)
                        # Unpack nested collections inside profile element
                        self._unpack_profile_element(el, entities)


        # 2. Collect entities from Profile View API response
        if payload.view_response and payload.view_response.json_data:
            data = payload.view_response.json_data
            if "included" in data and isinstance(data["included"], list):
                entities.extend(data["included"])
            if "profile" in data and isinstance(data["profile"], dict):
                entities.append(data["profile"])

        # 3. Parse embedded JSON <code> / <script> tags from HTML if available
        if payload.html_response and payload.html_response.html_content:
            html_text = payload.html_response.html_content
            import html as html_lib

            # A. Search for embedded JSON in <code> blocks
            code_blocks = re.findall(r"<code[^>]*>(.*?)</code>", html_text, re.DOTALL)
            for block in code_blocks:
                content = html_lib.unescape(block.strip())
                if content.startswith("{") and content.endswith("}"):
                    try:
                        parsed = json.loads(content)
                        if isinstance(parsed, dict):
                            if "included" in parsed and isinstance(parsed["included"], list):
                                entities.extend(parsed["included"])
                            if "data" in parsed and isinstance(parsed["data"], dict):
                                entities.append(parsed["data"])
                            else:
                                entities.append(parsed)
                    except Exception:
                        pass

            # B. Search for JSON-LD schema blocks
            ld_blocks = re.findall(
                r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                html_text,
                re.DOTALL | re.IGNORECASE,
            )
            for ld in ld_blocks:
                try:
                    ld_parsed = json.loads(html_lib.unescape(ld.strip()))
                    if isinstance(ld_parsed, list):
                        entities.extend(ld_parsed)
                    elif isinstance(ld_parsed, dict):
                        entities.append(ld_parsed)
                except Exception:
                    pass

        return entities

    def _unpack_profile_element(
        self, profile_el: dict[str, Any], entities: list[dict[str, Any]]
    ) -> None:
        """Extracts nested collections (positions, educations, skills, certs)
        from a profile element.
        """
        # 1. Position Groups & Positions

        pos_groups = profile_el.get("profilePositionGroups", {})
        if isinstance(pos_groups, dict):
            for group in pos_groups.get("elements", []):
                if isinstance(group, dict):
                    company_name = group.get("companyName") or group.get("name")
                    company_url = group.get("url") or (
                        group.get("company", {}).get("url")
                        if isinstance(group.get("company"), dict)
                        else None
                    )
                    sub_pos_group = (
                        group.get("profilePositionInPositionGroup")
                        or group.get("profilePositions")
                    )
                    if isinstance(sub_pos_group, dict) and sub_pos_group.get("elements"):
                        for p in sub_pos_group.get("elements", []):
                            if isinstance(p, dict):
                                if company_name and "companyName" not in p:
                                    p["companyName"] = company_name
                                if company_url and "companyUrl" not in p:
                                    p["companyUrl"] = company_url
                                entities.append(p)
                    else:
                        entities.append(group)


        # 2. Educations
        educations = profile_el.get("profileEducations", {})
        if isinstance(educations, dict):
            for edu in educations.get("elements", []):
                if isinstance(edu, dict):
                    entities.append(edu)

        # 3. Skills
        skills = profile_el.get("profileSkills", {})
        if isinstance(skills, dict):
            for sk in skills.get("elements", []):
                if isinstance(sk, dict):
                    entities.append(sk)

        # 4. Certifications
        certs = profile_el.get("profileCertifications", {})
        if isinstance(certs, dict):
            for cert in certs.get("elements", []):
                if isinstance(cert, dict):
                    entities.append(cert)

        # 5. Languages
        langs = profile_el.get("profileLanguages", {})
        if isinstance(langs, dict):
            for lang in langs.get("elements", []):
                if isinstance(lang, dict):
                    entities.append(lang)

