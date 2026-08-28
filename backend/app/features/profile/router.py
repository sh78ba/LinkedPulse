from fastapi import APIRouter, Depends

from app.features.profile.schemas import ProfileRequest, ProfileResponse
from app.features.profile.service import ProfileService

router = APIRouter(prefix="/profile", tags=["Profile"])


def get_profile_service() -> ProfileService:
    return ProfileService()


@router.post(
    "",
    response_model=ProfileResponse,
    summary="Retrieve LinkedIn Profile Information",
    description=(
        "Accepts a valid LinkedIn profile URL and returns normalized profile details "
        "including experience, education, skills, certifications, and languages "
        "via direct HTTP requests."
    ),
    responses={
        200: {"description": "Profile data successfully extracted and normalized."},
        400: {"description": "Invalid LinkedIn URL or bad request structure."},
        401: {"description": "LinkedIn authentication session expired or missing."},
        404: {"description": "LinkedIn profile not found or private."},
        429: {"description": "LinkedIn rate limit or verification checkpoint encountered."},
    },
)
async def get_profile(
    request: ProfileRequest,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Fetch and return reverse-engineered LinkedIn profile data."""
    return await service.get_profile(request.url)
