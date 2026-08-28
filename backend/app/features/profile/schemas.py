from pydantic import BaseModel, Field


class ProfileRequest(BaseModel):
    url: str = Field(
        ...,
        description="Full LinkedIn profile URL (e.g., https://www.linkedin.com/in/example/)",
        examples=["https://www.linkedin.com/in/williamhgates/"],
    )


class Image(BaseModel):
    url: str
    width: int | None = None
    height: int | None = None


class Profile(BaseModel):
    name: str | None = None
    headline: str | None = None
    location: str | None = None
    about: str | None = None
    profile_url: str | None = None
    images: list[str] = Field(default_factory=list)


class Experience(BaseModel):
    title: str | None = None
    company: str | None = None
    company_url: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class Education(BaseModel):
    school: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class Skill(BaseModel):
    name: str


class Certification(BaseModel):
    name: str | None = None
    authority: str | None = None
    license_number: str | None = None
    url: str | None = None
    issue_date: str | None = None
    expiration_date: str | None = None


class Language(BaseModel):
    name: str | None = None
    proficiency: str | None = None


class ProfileResponse(BaseModel):
    success: bool = True
    profile: Profile = Field(default_factory=Profile)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
